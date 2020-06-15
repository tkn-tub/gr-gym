import abc


# TODO
class gnu_case(abc.ABC):

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
    def execute_actions(self):
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
    def simulate(self):
        pass
