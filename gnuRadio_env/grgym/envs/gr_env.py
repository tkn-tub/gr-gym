import importlib
import logging
import time
import xmlrpc.client
import signal
import sys
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
        
        root_dir = get_dir_by_indicator(indicator=".git")
        yaml_path = str(Path(root_dir) / "params" / "config.yaml")
        self.args = yaml_argparse(yaml_path=yaml_path)
        
        self.bridge = GR_Bridge(self.args.rpchost, self.args.rpcport)
        
        modules = self.args.scenario.split(".") 
        module = importlib.import_module("grgym.scenarios." + ".".join(modules[0:-1]))
        gnu_module = getattr(module, modules[-1]) # need a python 3 version
        
        self.scenario = gnu_module(self.bridge, self.args)
        
        # TODO: compile and start .grc file (UniFlex Module)

        self.action_space = None
        self.observation_space = None
        
        self.gr_state = RadioProgramState.INACTIVE

        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()
        
        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

    def _init_proxy(self):
        if self.ctrl_socket == None:
            self.ctrl_socket = xmlrpc.client.ServerProxy(
                "http://%s:%d" % (self.ctrl_socket_host, self.ctrl_socket_port))

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        if self.check_is_alive():
            self._logger.info("send action to gnuradio")
            self.scenario.execute_actions(action)
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
                    print("Please start the GNU Radio scenario")
                    time.sleep(10)
                self._logger.error("Multiple Start Error %s" % (e))
        self.gr_state = RadioProgramState.RUNNING
        self.scenario.reset()
        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()
        time.sleep(self.args.simTime)
        obs = self.scenario.get_obs()

        return obs
    
    def handle_termination(self, signum, frame):
        self.bridge.close()
        self.close()
        sys.exit(1)
    
    def close(self):
        if self.check_is_alive():
            self._logger.info("Stop grc execution")
            self.gr_state = RadioProgramState.INACTIVE
        pass

    def render(self, mode='human'):
        return

    def check_is_alive(self):
        if self.gr_state == RadioProgramState.INACTIVE:
            return False
        if self.gr_state == RadioProgramState.RUNNING:
            return True
