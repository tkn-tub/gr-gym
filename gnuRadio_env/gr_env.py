import importlib
import logging
import time
import xmlrpc.client

import gym
from gym.utils import seeding

from gnuRadio_env.ieee80211codemodscenario import *
from utils import *


class gr_env(gym.Env):
    def __init__(self, args, gnuradio, scenario):
        super(gr_env, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self.args = args
        self.gnuradio = gnuradio
        self.scenario = scenario

        self.action_space = None
        self.observation_space = None

        self.gr_radio_programs_path = args.rpc.gr_radio_programs_path
        self.gr_state = self.gnuradio.RadioProgramState.INACTIVE
        self.usrp_addr = args.rpc.usrp_addr

        self.ctrl_socket_host = args.rpc.host
        self.ctrl_socket_port = args.rpc.port

        self.ctrl_socket = None
        if self.gr_state == self.gnuradio.RadioProgramState.INACTIVE:
            self._logger.info("start gnuradio ")
            self._init_proxy()
            self.ctrl_socket.start()
            self.gr_state = self.gnuradio.RadioProgramState.RUNNING
            self._logger.debug(f"Information of the rpc client: {self.ctrl_socket.__dict__}")

        elif self.gr_state == self.gnuradio.RadioProgramState.PAUSED:
            self._logger.info("wake up gnuradio")
            self._init_proxy()
            self.ctrl_socket.start()
            self.gr_state = self.gnuradio.RadioProgramState.RUNNING

        self.action_space = self.scenario.get_actions_space()
        self.observation_space = self.scenario.get_observation_space()

    def _init_proxy(self):
        if self.ctrl_socket == None:
            self.ctrl_socket = xmlrpc.client.ServerProxy(
                "http://%s:%d" % (self.ctrl_socket_host, self.ctrl_socket_port))

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_state(self):
        # get state on timestep k+1
        obs = self.scenario.get_obs()
        reward = self.scenario.get_reward()
        info = self.scenario.get_info()
        done = self.scenario.get_done()
        return (obs, reward, info, done)

    def step(self, action):
        # TODO set a waiting time btw sending action and geting observation
        if self.check_is_alive():
            self._logger.info("send action to gnuradio")
            self.scenario.send_actions(action)
            self._logger.info("wait for step time")
            time.sleep(args.stepTime)
            self._logger.info("get reward")
            reward = self.scenario.get_reward()
            done = self.scenario.get_done()
            info = self.scenario.get_info()
            self._logger.info("start simuation in gnu radio")
            self.scenario.simulate()
            self._logger.info("wait for simulation")
            time.sleep(args.simTime)
            self._logger.info("collect observations")
            obs = self.scenario.get_obs()

        if self.check_is_alive():
            pass

        return (obs, reward, done, info)

    def reset(self):
        # TODO reset proxy connection
        #
        self._logger.info("reset usecase scenario")
        if self.scenario:
            self.scenario.close()
            self.scenario = None
        # self.scenario = scenario
        self.scenario.reset()
        self.action_space = self.scenario.get_action_space()
        self.observation_space = self.scenario.get_observation_space()

        return

    def close(self):
        pass

    def render(self, mode='human'):
        return

    def check_is_alive(self):
        if self.gr_state == self.gnuradio.RadioProgramState.INACTIVE:
            return False
        if self.gr_state == self.gnuradio.RadioProgramState.RUNNING:
            return True


if __name__ == "__main__":
    root_dir = get_dir_by_indicator(indicator=".git")
    yaml_path = str(Path(root_dir) / "params" / "ieee80211p.yaml")
    args = yaml_argparse(yaml_path=yaml_path)


    modules = args.gnu_radio_program.split(".") # TODO use import module from config file
    module = importlib.import_module(".".join(modules[0:-1]))
    gnu_module = getattr(module, modules[-1]) # need a python 3 version
    ieee80211p = ieee80211_scenario(gnu_module)


    gnu_env = gr_env(args=args, gnuradio=gnu_module, scenario=ieee80211p)
