'''
A scenario based on the gr-80211 gnu radio implementation showcasing rate adaptation.
Designed to run locally, i.e. transmitter and receiver are connected via simulated channel (loopback)

Sascha Rösler <s.roesler@campus.tu-berlin.de>
Tien Dat Phan <t.phan@campus.tu-berlin.de>
Anatolij Zubow <zubow@tkn.tu-berlin.de>
'''
from gym import spaces
import numpy as np
from grgym.envs.gnu_case import gnu_case
from grgym.envs.gr_bridge import BridgeConnectionType
from datetime import datetime

class ieee80211_scenario(gnu_case):
    def __init__(self, gnuradio, conf):
        super().__init__(gnuradio, conf)
        self.debug = False
        self.name = 'gr-gnugym-80211-mcs-selection'

        if not self.conf.grgym_environment.run_local:
            # in remote mode we assume that full gnuradio is running on first remote node
            self.gnuradio = self.gnuradio[0]
            print('%s:: connecting to remote node %s' % (self.name, self.gnuradio.host))

        # state variables
        self.last_send_pkt_cnt = 0
        self.last_recv_pkt_cnt = 0
        self.no_packet_rx_within_step_cnt = 0 # count the number of steps without a single packet received
        self.last_done_pkt_recv_cnt = 0
        self.last_obs_time = 0
        self.step_count = 0

        # TODO: refactor
        self.low = 10.0
        self.high = 35.0

        # bitrates available in 802.11p GnuRadio stack; position is the MCS index
        self.bitrates = [
            3.0,  # Mbps MCS0: BPSK 1/2
            4.5,  # Mbps MCS1: BPSK 3/4
            6.0,  # Mbps MCS2: QPSK 1/2
            9.0,  # Mbps MCS3: QPSK 3/4
            12.0,  # Mbps MCS4: 16QAM 1/2
            18.0,  # Mbps MCS5: 16QAM 3/4
            24.0,  # Mbps MCS6: 64QAM 2/3
            27.0  # Mbps MCS7: 64QAM 3/4
        ]

        self.mcs = list(conf.grgym_scenario.mcs)
        if self.debug:
            print('%s:: Available MCS: %s' % (self.name, str(self.mcs)))

        # mapping table from action ID to MCS index; only bitrates from this table are available
        # see config.yaml file for configuration
        self.act_to_idx = dict()
        for id, mcs in enumerate(self.mcs):
            self.act_to_idx[id] = mcs

        self.NSC = 64 # no. OFDM subcarriers

        # IPC with GnuRadio process to collect observations and data needed to calculate the reward
        if False and self.conf.grgym_environment.run_local:
            # use named pipes if processes running on same machine
            self.gnuradio.subscribe_parameter('pkt_snd_cnt', '/tmp/pkt_snd_cnt', np.int32, 1, BridgeConnectionType.PIPE)
            self.gnuradio.subscribe_parameter('pkt_recv_cnt', '/tmp/pkt_recv_cnt', np.int32, 1, BridgeConnectionType.PIPE)
            self.gnuradio.subscribe_parameter('rssi_obs', '/tmp/rssi_obs', np.float32, self.NSC, BridgeConnectionType.PIPE)
        else:
            # ZMQ for remote IPC
            self.gnuradio.subscribe_parameter('pkt_snd_cnt', 8001, np.int32, 1, BridgeConnectionType.ZMQ)
            self.gnuradio.subscribe_parameter('pkt_recv_cnt', 8002, np.int32, 1, BridgeConnectionType.ZMQ)
            self.gnuradio.subscribe_parameter('rssi_obs', 8003, np.float32, self.NSC, BridgeConnectionType.ZMQ)

    def get_observation_space(self):
        return spaces.Box(low=self.low, high=self.high, shape=(self.NSC, 1), dtype=np.float32)

    def get_action_space(self):
        return spaces.Discrete(len(self.act_to_idx))

    def execute_action(self, action):
        # map action ID to MCS index
        mcs_idx = self.act_to_idx[action]
        if self.debug:
            print('%s::%s. execute_action: MCS idx: %d' % (self.name, datetime.now().time(), mcs_idx))

        # set MCS/bitrate on GnuRadio process
        self.gnuradio.set_parameter('encoding', int(mcs_idx))

    def _get_reward_state(self, eventbased):
        # get Data of gnuradio
        if eventbased:
            self.gnuradio.wait_for_value('pkt_recv_cnt')

        # get packet counters to TX and RX side so that we can compute PER later
        pkt_snd_cnt = self.gnuradio.get_parameter('pkt_snd_cnt')
        pkt_snd_cnt = pkt_snd_cnt[0][0]
        pkt_recv_cnt = self.gnuradio.get_parameter('pkt_recv_cnt')
        pkt_recv_cnt = pkt_recv_cnt[0][0]

        total_send = pkt_snd_cnt - self.last_send_pkt_cnt
        total_recv = pkt_recv_cnt - self.last_recv_pkt_cnt

        if self.debug:
            print("d_snd/recv/miss: %d/%d" % (total_send, total_recv))

        self.last_send_pkt_cnt = pkt_snd_cnt
        self.last_recv_pkt_cnt = pkt_recv_cnt

        return total_send, total_recv

    def get_obs(self):
        if self.conf.grgym_environment.eventbased:
            self.gnuradio.wait_for_value('rssi_obs')

        if self.debug:
            print('%s::%s. get_obs' % (self.name, datetime.now().time()))

        (obs, time) = self.gnuradio.get_parameter('rssi_obs')

        if time - self.last_obs_time == 0:
            print("%s:: Warning: processing old observation caused by too slow CPU" % (self.name))
            return np.full((1, self.NSC), self.low)[0]

        self.last_obs_time = time

        self.gnuradio.wait_for_value('rssi_obs')
        (obs2, time) = self.gnuradio.get_parameter('rssi_obs')

        # compute average over two observations
        avg = np.full((1, self.NSC), self.low)[0]
        for i in range(self.NSC):
            avg[i] = np.average([obs[i], obs2[i]])

        (totalSend, totalRecv) = self._get_reward_state(False)
        return avg[-self.NSC:]

    def get_reward(self):
        if self.debug:
            print('%s::%s. get_reward' % (self.name, datetime.now().time()))

        encoding = self.gnuradio.get_parameter('encoding')[0]
        assert encoding >= 0 and encoding < len(self.bitrates)

        (totalSend, totalRecv) = self._get_reward_state(self.conf.grgym_environment.eventbased)
        # calculate effective throughput, i.e. packet success rate x bitrate
        return float(totalRecv) / (totalSend + 1) * self.bitrates[encoding]

    def get_done(self):
        pkt_recv_cnt = self.gnuradio.get_parameter('pkt_recv_cnt')
        pkt_recv_cnt = pkt_recv_cnt[0][0]

        if pkt_recv_cnt == self.last_done_pkt_recv_cnt:
            self.no_packet_rx_within_step_cnt += 1
        else:
            self.no_packet_rx_within_step_cnt = 0 # reset to 0

        self.last_done_pkt_recv_cnt = pkt_recv_cnt

        if self.no_packet_rx_within_step_cnt >= self.conf.grgym_environment.max_steps_zero_reward:
            # give up episode due to no reception during last max_steps_zero_reward steps
            return True

        return False

    def render(self):
        # no GUI so far
        return

    def reset(self):
        # set initial action
        self.execute_action(0) # reset to lowest action/MCS
        self.gnuradio.set_parameter('snr', self.conf.grgym_scenario.channel_SNR)
        self.gnuradio.set_parameter('interval', self.conf.grgym_scenario.packet_interval)

        # reset local counter
        self._get_reward_state(False)
        self.no_packet_rx_within_step_cnt = 0
        self.last_done_pkt_recv_cnt = 0
        self.step_count = 0
        self.last_obs_time = 0

    def get_info(self):
        return self.name

    def sim_channel(self):
        '''
        In loopback mode the channel is simulated and changed here.
        '''

        if not self.conf.grgym_local.simulation.simulate_channel:
            return

        if self.debug:
            print('%s::%s. simulate_channel' % (self.name, datetime.now().time()))

        if self.step_count % self.conf.grgym_local.simulation.longterm_channel_coherence_time == 0:
            # simple block model, i.e. channel stays the same for sim_steps & afterwards a random value for the
            # attenuation is selected
            dist = np.random.uniform(self.conf.grgym_local.simulation.sim_channel_min_dist, self.conf.grgym_local.simulation.sim_channel_max_dist)
            # set on Gnuradio process
            self.gnuradio.set_parameter("dist", dist)

        self.step_count += 1
        return
