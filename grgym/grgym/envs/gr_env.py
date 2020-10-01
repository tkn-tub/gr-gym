'''
The generic Gr-Gym environment which delegates the calls to the specific scenario.

Anatolij Zubow <zubow@tkn.tu-berlin.de>
Ali Alouane <ali.alouane@campus.tu-berlin.de>
Sascha Rösler <s.roesler@campus.tu-berlin.de>
'''

import importlib
import logging
import subprocess
import time
import signal
import sh
from enum import Enum

import gym
from gym.utils import seeding
from grgym.envs.gr_bridge import GR_Bridge
from grgym.envs.gr_utils import *

# keep track of gnuradio process state
class RadioProgramState(Enum):
    INACTIVE = 1
    RUNNING = 2

class GrEnv(gym.Env):
    def __init__(self, config_file='config.yaml'):
        super(GrEnv, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        print('Starting GrGym ... ')

        # parse configuration from yaml config file
        self.example_dir = Path(os.getcwd()).parent
        yaml_path = str(self.example_dir / config_file)
        self.conf = parse_yaml(yaml_path=yaml_path)

        self.gr_state = RadioProgramState.INACTIVE
        # so far only tested in local mode
        if self.conf.grgym_environment.run_local:
            # setup bridge to communicate with Gnuradio processes
            self.bridge = GR_Bridge(self.conf.grgym_local.host, self.conf.grgym_local.rpc_port)

            # compile grc file and start Gnuradio program if run locally
            if self.conf.grgym_local.compile_and_start_gr:
                self.gr_process = None
                self.gr_process_io = None
                # compile grc
                self._local_compile_radio_program(str(self.example_dir / 'grc'),
                                                  self.conf.grgym_local.gr_grc)
                # start gr
                self._local_start_radio_program(str(self.example_dir / 'grc'),
                                                self.conf.grgym_local.gr_grc)
        else:
            # remote mode; create list of bridges
            self.num_nodes = self.conf.grgym_remote.num_nodes
            self.bridge = []
            for node in range(self.num_nodes):
                host = self.conf.grgym_remote['node' + str(node)].host
                rpc_port = self.conf.grgym_remote['node' + str(node)].rpc_port
                self.bridge.append(GR_Bridge(host, rpc_port))

        # init grgym scenario
        modules = self.conf.grgym_scenario.scenario_class.split(".")
        module = importlib.import_module("grgym.scenarios." + ".".join(modules[0:-1]))
        gnu_module = getattr(module, modules[-1])  # need a python 3 version
        self.scenario = gnu_module(self.bridge, self.conf)

        # init gym
        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()

        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

    '''
        Gym framework function
    '''
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    '''
        Gym framework function
    '''
    def step(self, action):
        self._logger.info("grgym::step()")

        if self.conf.grgym_environment.run_local and not self.check_is_alive():
            print('Warning: calling step on a dead Gnuradio process')

        # delegate to scenario class
        self.scenario.execute_action(action)

        if not self.conf.grgym_environment.eventbased:
            self._logger.info("grgym::timebased: wait for step time")
            time.sleep(self.conf.grgym_environment.timebased.step_time)

        self._logger.info("collect results (reward, done, info) from scenario")
        reward = self.scenario.get_reward()
        done = self.scenario.get_done()
        info = self.scenario.get_info()

        if self.conf.grgym_environment.run_local and self.conf.grgym_local.simulation.simulate_channel:
            self._logger.info("grgym::sim_channel in local gnuradio process")
            self.scenario.sim_channel()
            # Call get_obs to reset internal states
            if not self.conf.grgym_environment.eventbased:
                self.scenario.get_obs()
                self._logger.info("grgym::sim_channel: wait for simulation step")
                time.sleep(self.conf.grgym_local.simulation.sim_time)

        self._logger.info("grgym::collect observations")
        obs = self.scenario.get_obs()

        return (obs, reward, done, info)

    '''
        Gym framework function
    '''
    def reset(self):
        self._logger.info("grgym::reset()")

        # start gnuradio using the bridge if grnuradio not yet running
        if not self.check_is_alive():
            error = True
            while error is True:
                error = False
                try:
                    if self.conf.grgym_environment.run_local:
                        self.bridge.start()
                    else:
                        # remote mode: start all bridges
                        for br in self.bridge:
                            br.start()
                except Exception as e:
                    if type(e) is ConnectionRefusedError:
                        # no rpc server
                        error = True
                        if self.conf.grgym_local.compile_and_start_gr:
                            print("Wait for start of GNU-Radio. This should happen automatically.")
                        else:
                            print("Wait for start of GNU-Radio. Please start the scenario on the other machine now.")
                        time.sleep(10)
                    self._logger.error("Multiple Start Error %s" % (e))

        time.sleep(2) # wait to gnuradio to settle down
        self.gr_state = RadioProgramState.RUNNING
        self.scenario.reset()

        if not self.conf.grgym_environment.eventbased:
            if self.conf.grgym_local.simulation.simulate_channel:
                time.sleep(self.conf.grgym_local.simulation.sim_time)
        obs = self.scenario.get_obs()

        return obs

    '''
        Gym framework function
    '''
    def close(self):
        if self.conf.grgym_environment.run_local:
            self.bridge.close()
        else:
            for br in self.bridge:
                br.close()

        if self.check_is_alive():
            self._logger.info("Stop grc execution")
            if self.conf.grgym_environment.run_local:
                self._local_stop_radio_program()
                self.gr_state = RadioProgramState.INACTIVE
        pass

    '''
        Gym framework function
    '''
    def render(self, mode='human'):
        return

    def check_is_alive(self):
        if self.gr_state == RadioProgramState.INACTIVE:
            return False
        if self.gr_state == RadioProgramState.RUNNING:
            return True

    def handle_termination(self, signum, frame):
        self.close()
        sys.exit(1)

    #
    # Helper methods for local handling of gnuradio
    #

    def _local_compile_radio_program(self, gr_radio_programs_path, grc_radio_program_name):
        grProgramPath = os.path.join(gr_radio_programs_path, grc_radio_program_name + '.grc')

        print('Compiling grc file: %s' % (str(grProgramPath)))
        # if version.parse(gr.version()) > version.parse('3.8.0'):
        outdir = "--output=%s" % gr_radio_programs_path
        # else:
        #    outdir = "--directory=%s" % gr_radio_programs_path
        try:
            sh.grcc(outdir, grProgramPath)
        except Exception as e:
            raise
        self._logger.info("Compilation Completed")

    def _local_start_radio_program(self, gr_radio_programs_path, grc_radio_program_name):
        if self.gr_process_io is None:
            self.gr_process_io = {'stdout': open('/tmp/gnuradio.log', 'w+'),
                                  'stderr': open('/tmp/gnuradio-err.log', 'w+')}
        try:
            print('Starting Gnuradio file: %s' % (str(grc_radio_program_name)))
            # start GNURadio process
            print("For the gnuradio process, see:\n\t/tmp/gnuradio.log and \n\t/tmp/gnuradio-err.log")
            pyRadioProgPath = os.path.join(gr_radio_programs_path, grc_radio_program_name + '.py')
            self._logger.info("Start radio program: {}".format(pyRadioProgPath))
            self.gr_radio_program_name = grc_radio_program_name
            self.gr_process = subprocess.Popen(["env", "python3", pyRadioProgPath],
                                               stdout=self.gr_process_io['stdout'], stderr=self.gr_process_io['stderr'])
            self.gr_state = RadioProgramState.RUNNING
        except OSError:
            return False
        return True

    def _local_stop_radio_program(self):
        if self.check_is_alive():
            self._logger.info("stopping radio program")

            if self.gr_process is not None and hasattr(self.gr_process, "kill"):
                self.gr_process.kill()

            if self.gr_process_io is not None and self.gr_process_io is dict:
                for k in self.gr_process_io.keys():
                    # if self.gr_process_io[k] is file and not self.gr_process_io[k].closed:
                    if not self.gr_process_io[k].closed:
                        self.gr_process_io[k].close()
                        self.gr_process_io[k] = None
            self.gr_state = RadioProgramState.INACTIVE
