import gym
from gym.utils import seeding
from gym import spaces
from utils import *
import pandas as pb
import abc


class RpcBridge():
    def __init__(self, args):
        pass


class gr_env(gym.Env):
    def __init__(self, args):
        super(gr_env, self).__init__()
        self.args = args

        self.action_space = None
        self.observation_space = None

        self.rpcBridge = RpcBridge(self.args.rpc)
        self.senario = IEEE80211P(self.args.ieee80211p)
        self.action_space = self.senario.get_actions_space()
        self.observation_space = self.senario.get_observation_space()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_state(self):
        obs = self.senario.get_obs()
        reward = self.senario.get_reward()
        info = self.senario.get_info()
        done = self.senario.get_done()
        return (obs, reward, info, done)

    def step(self, action):
        response = self.senario.step(action)
        return self.get_state()

    def reset(self):
        if self.senario:
            self.senario.close()
            self.senario = None
        self.senario = IEEE80211P(self.args.ieee80211p)
        self.senario.initialize_env()
        self.action_space = self.senario.get_actions_space()
        self.observation_space = self.senario.get_observation_space()
        pass

    def close(self):
        pass


class IEEE80211(abc.ABC):
    @abc.abstractmethod
    def initialize_env(self):
        pass


class IEEE80211P(IEEE80211):
    def __init__(self, args):
        super(IEEE80211P, self).__init__()
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
        if (spaceDesc.type == pb.Box):
            boxSpacePb = pb.BoxSpace()
            spaceDesc.space.Unpack(boxSpacePb)
            low = boxSpacePb.low
            high = boxSpacePb.high
            shape = tuple(boxSpacePb.shape)
            mtype = boxSpacePb.dtype

        space = spaces.Box(low=low, high=high, shape=shape, dtype=mtype)


    def initialize_env(self):
        self._action_space = self._create_space()
        self._observation_space = self._create_space()

    def send_actions(self, actions):
        pass


    def step(self, actions):
        self.send_actions(actions)

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
