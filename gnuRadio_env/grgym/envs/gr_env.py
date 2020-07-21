'''
gnugym project, TU-Berlin 2020
Ali Alouane <ali.alouane@campus.tu-berlin.de>
Sascha Rösler <s.roesler@campus.tu-berlin.de>
'''
import importlib
import logging
import subprocess
import time
import xmlrpc.client
import signal
import sys
import sh
import os
from enum import Enum

import gym
from gym.utils import seeding
from grgym.envs.gr_bridge import GR_Bridge

from grgym.envs.gr_utils import *

class RadioProgramState(Enum):
    INACTIVE = 1
    RUNNING = 2
    PAUSED = 3
    STOPPED = 4

class GrEnv(gym.Env):
    def __init__(self):
        super(GrEnv, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self.gr_process = None
        self.gr_process_io = None
        
        #read configuration from yaml
        self.root_dir = get_dir_by_indicator(indicator=".git")
        yaml_path = str(Path(self.root_dir) / "params" / "config.yaml")
        self.args = yaml_argparse(yaml_path=yaml_path)
        
        self.bridge = GR_Bridge(self.args.rpchost, self.args.rpcport)
        
        #compile and start gnuradio
        if self.args.radio_programs_compile_execute:
            self._compile_radio_program(str(Path(self.root_dir) / self.args.radio_programs_path), self.args.gnu_radio_program_filename)
            self._start_radio_program(str(Path(self.root_dir) / self.args.radio_programs_path), self.args.gnu_radio_program)
        
        modules = self.args.scenario.split(".") 
        module = importlib.import_module("grgym.scenarios." + ".".join(modules[0:-1]))
        gnu_module = getattr(module, modules[-1]) # need a python 3 version
        
        self.scenario = gnu_module(self.bridge, self.args)

        self.action_space = None
        self.observation_space = None
        
        self.gr_state = RadioProgramState.INACTIVE

        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()
        
        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        if self.check_is_alive():
            self._logger.info("send action to gnuradio")
            self.scenario.execute_actions(action)
            if not self.args.eventbased:
                self._logger.info("wait for step time")
                time.sleep(self.args.stepTime)
            self._logger.info("get reward")
            reward = self.scenario.get_reward()
            done = self.scenario.get_done()
            info = self.scenario.get_info()
            if self.args.simulate == True:
                self._logger.info("start simuation in gnu radio")
                self.scenario.simulate()
                #Call get_obs to reset internal states
                if not self.args.eventbased:
                    self.scenario.get_obs()
                    self._logger.info("wait for simulation")
                    time.sleep(self.args.simTime)
            self._logger.info("collect observations")
            obs = self.scenario.get_obs()

        if self.check_is_alive():
            pass

        return (obs, reward, done, info)
    
    def reset(self):
        self._logger.info("reset usecase scenario")
        self.scenario.reset()
        error = True
        while error is True:
            error = False
            try:
                self.bridge.start()
            except Exception as e:
                if type(e) is ConnectionRefusedError:
                    # no rpc server
                    error = True
                    if self.args.radio_programs_compile_execute:
                        print("Wait for start of GNU-Radio. This should happen automaticaly.")
                    else:
                        print("Wait for start of GNU-Radio. Please start the scenario on the other machine now.")
                    time.sleep(10)
                self._logger.error("Multiple Start Error %s" % (e))
        self.gr_state = RadioProgramState.RUNNING
        self.scenario.reset()
        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()
        if not self.args.eventbased:
            time.sleep(self.args.simTime)
        obs = self.scenario.get_obs()

        return obs
    
    def handle_termination(self, signum, frame):
        self.close()
        sys.exit(1)
    
    def close(self):
        self.bridge.close()
        if self.check_is_alive():
            self._logger.info("Stop grc execution")
            self._stop_radio_program()
            self.gr_state = RadioProgramState.INACTIVE
        pass

    def render(self, mode='human'):
        return

    def check_is_alive(self):
        if self.gr_state == RadioProgramState.INACTIVE:
            return False
        if self.gr_state == RadioProgramState.RUNNING:
            return True
    
    def _compile_radio_program(self, gr_radio_programs_path, grc_radio_program_name):
        grProgramPath = os.path.join(gr_radio_programs_path, grc_radio_program_name + '.grc')
        outdir = "--directory=%s" % gr_radio_programs_path
        try:
            sh.grcc(outdir, grProgramPath)
        except Exception as e:
            raise
        self._logger.info("Compilation Completed")
    
    def _start_radio_program(self, gr_radio_programs_path, grc_radio_program_name):
        if self.gr_process_io is None:
            self.gr_process_io = {'stdout': open('/tmp/gnuradio.log', 'w+'), 'stderr': open('/tmp/gnuradio-err.log', 'w+')}
        try:
            # start GNURadio process
            pyRadioProgPath = os.path.join(gr_radio_programs_path, grc_radio_program_name + '.py')
            self._logger.info("Start radio program: {}".format(pyRadioProgPath))
            self.gr_radio_program_name = grc_radio_program_name
            self.gr_process = subprocess.Popen(["env", "python2", pyRadioProgPath],
                                               stdout=self.gr_process_io['stdout'], stderr=self.gr_process_io['stderr'])
            self.gr_state = RadioProgramState.RUNNING
        except OSError:
            return False
        return True
        
    def _stop_radio_program(self):
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
