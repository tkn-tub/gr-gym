'''
A scenario based on the gr-80211 gnu radio implementation used for benchmarking, i.e. computing the
step duration in different configurations.

Anatolij Zubow <zubow@tkn.tu-berlin.de>
'''
from gym import spaces
import numpy as np
from grgym.envs.gr_scenario import GrScenario
from grgym.envs.gr_bridge import BridgeConnectionType
from datetime import datetime

class BenchmarkScenario(GrScenario):
    def __init__(self, gnuradio, conf):
        super().__init__(gnuradio, conf)
        self.debug = False
        self.name = 'gr-gnugym-benchmark'

        if not self.conf.grgym_environment.run_local:
            # in remote mode we assume that full gnuradio is running on first remote node
            self.gnuradio = self.gnuradio[0]
            print('%s:: connecting to remote node %s' % (self.name, self.gnuradio.host))

        # IPC with GnuRadio process to collect observations and data needed to calculate the reward
        if self.conf.grgym_environment.run_local and self.conf.grgym_local.gr_ipc == 'FILE':
            # use named pipes if processes running on same machine
            print('Use named pipes')
            self.gnuradio.subscribe_parameter('obs', '/tmp/obs', np.float32, self.conf.grgym_scenario.obs_len, BridgeConnectionType.PIPE)
        else:
            # ZMQ for remote IPC
            print('Use ZMQ')
            self.gnuradio.subscribe_parameter('obs', 8001, np.float32, self.conf.grgym_scenario.obs_len, BridgeConnectionType.ZMQ)

    def get_observation_space(self):
        return spaces.Box(low=0, high=7, shape=(1, 1), dtype=np.int)

    def get_action_space(self):
        return spaces.Discrete(8)

    def execute_action(self, action):
        # set action on GnuRadio process
        if self.debug:
            print('action: %d' % action)
        self.gnuradio.set_parameter('encoding', action)

    def get_obs(self):
        (obs, time) = self.gnuradio.get_parameter('obs')
        return obs

    def get_reward(self):
        return 1

    def get_done(self):
        return False

    def render(self):
        # no GUI so far
        return

    def reset(self):
        if self.debug:
            print('obs_len: %d' % self.conf.grgym_scenario.obs_len)
            print('interval: %d' % self.conf.grgym_scenario.packet_interval)

        self.gnuradio.set_parameter('interval', self.conf.grgym_scenario.packet_interval)
        self.gnuradio.set_parameter('obs_len', self.conf.grgym_scenario.obs_len)

    def get_info(self):
        return self.name

    def sim_channel(self):
        pass
