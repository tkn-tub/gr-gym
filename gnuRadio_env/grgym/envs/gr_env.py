import importlib
import logging
import time
import xmlrpc.client
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
        # TODO: change name of config file
        yaml_path = str(Path(root_dir) / "params" / "ieee80211p.yaml")
        self.args = yaml_argparse(yaml_path=yaml_path)
        
        self.bridge = GR_Bridge(self.args.rpchost, self.args.rpcport)
        
        # TODO: Change location of scenario file
        modules = self.args.scenario.split(".") 
        module = importlib.import_module("grgym.envs." + ".".join(modules[0:-1]))
        gnu_module = getattr(module, modules[-1]) # need a python 3 version
        
        #TODO: put args to specific module
        self.scenario = gnu_module(self.bridge)
        
        # TODO: compile and start .grc file (UniFlex Module)

        self.action_space = None
        self.observation_space = None
        
        self.gr_state = RadioProgramState.INACTIVE

        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()

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
            self._logger.info("start simuation in gnu radio")
            self.scenario.simulate()
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
        try:
            self.bridge.start()
        except Exception as e:
            self._logger.error("Multiple Start Error %s" % (e))
        self.gr_state = RadioProgramState.RUNNING
        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()

        return

    def close(self):
        pass

    def render(self, mode='human'):
        return

    def check_is_alive(self):
        if self.gr_state == RadioProgramState.INACTIVE:
            return False
        if self.gr_state == RadioProgramState.RUNNING:
            return True
