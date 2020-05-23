import gym
from gym.utils import seeding
from gym import spaces
from utils import *
import pandas as pb
import abc
import xmlrpc.client
import logging
import time


class gr_env(gym.Env):
    def __init__(self, args, gnuradio):
        super(gr_env, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self.args = args
        self.gnuradio = gnuradio

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

        self.scenario = IEEE80211P(self.args.ieee80211p)
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
        if self.gr_state == self.gnuradio.RadioProgramState.RUNNING:
            self._logger.info("send action to gnuradio")
            self.scenario.send_actions(action)

    def reset(self):
        # TODO reset proxy connection
        #
        if self.scenario:
            self.scenario.close()
            self.scenario = None
        self.scenario = IEEE80211P(self.args.ieee80211p)
        self.scenario.initialize_env()
        self.action_space = self.scenario.get_actions_space()
        self.observation_space = self.scenario.get_observation_space()
        pass

    def close(self):
        pass

    def render(self, mode='human'):
        return

    def check_is_alive(self):
        if self.gr_state == self.gnuradio.RadioProgramState.INACTIVE:
            self.ctrl_socket = None


class IEEE80211(abc.ABC):
    @abc.abstractmethod
    def initialize_env(self):
        pass

    @abc.abstractmethod
    def send_actions(self):
        pass


class IEEE80211P(IEEE80211):
    def __init__(self, args):
        super(IEEE80211P, self).__init__()
        self.args = args
        self.sync_length = args.sync_length
        self.frequency = args.frequency
        self.bandwidth = args.bandwidth
        self.windows_size = args.windows_size

        self.reward = 0
        self.obsData = None
        self.done = False
        self.info = None

    def get_actions_space(self):
        return self._action_space

    def get_observation_space(self):
        return self._observation_space

    def _create_space(self, spaceDesc):
        space = None
        if spaceDesc.type == spaces.Discrete:
            space = spaces.Discrete(spaceDesc.n)
        if spaceDesc.type == spaces.Box:
            space = spaces.Box(low=spaceDesc.low, high=spaceDesc.high, shape=spaceDesc.shape, dtype=spaceDesc.mtype)
        return space

    def initialize_env(self):
        self._action_space = self._create_space(self.args.actSpace)
        self._observation_space = self._create_space(self.args.obsSpace)

    def send_actions(self, action):
        pass

    def get_subcarriers_stat(sefl):
        pass

    def get_packetcount(self):
        pass

    def get_reward(self):
        return self.reward

    def get_obs(self):
        return self.obsData

    def get_done(self):
        return self.done

    def get_info(self):
        return self.info

    def _create_data(self, dataContainer):
        pass

    def _pack_data(self, actions, spaceDesc):
        pass

    def close(self):
        pass
