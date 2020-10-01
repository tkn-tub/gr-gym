'''
The base class for all scenarios.

Anatolij Zubow <zubow@tkn.tu-berlin.de>
Ali Alouane <ali.alouane@campus.tu-berlin.de>
'''

import abc

class gnu_case(abc.ABC):
    @abc.abstractmethod
    def __init__(self, gnuradio, conf):
        """ Init your scenario
        """
        self.gnuradio = gnuradio
        self.conf = conf

    @abc.abstractmethod
    def get_observation_space(self):
        """Returns observation space
        """
        pass

    @abc.abstractmethod
    def get_action_space(self):
        """Returns action space
        """
        pass

    @abc.abstractmethod
    def execute_action(self, action):
        pass

    @abc.abstractmethod
    def get_obs(self):
        pass

    @abc.abstractmethod
    def get_reward(self):
        pass

    @abc.abstractmethod
    def get_done(self):
        pass

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def get_info(self):
        pass

    @abc.abstractmethod
    def sim_channel(self):
        pass
