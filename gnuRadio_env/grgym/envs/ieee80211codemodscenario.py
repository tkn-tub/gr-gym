from gym import spaces
import numpy as np
# TODO what is the interface class
from grgym.envs.gnu_case import gnu_case


class ieee80211_scenario(gnu_case):
    def __init__(self, gnuradio):
        self.gnuradio = gnuradio
        self.lastSendSeqnr = 0
        self.lastRecvSeqnr = 0
        self.lastMissingCounter = 0
        self.action = 0
        self.bitrates = [
            1.5,  # Mbps BPSK 1/2
            1.25,  # Mbps BPSK 3/4
            3,  # Mbps QPSK 1/2
            4.5,  # Mbps QPSK 3/4
            6,  # Mbps 16QAM 1/2
            9,  # Mbps 16QAM 3/4
            16,  # Mbps 64QAM 2/3
            18  # Mbps 64QAM 3/4
        ]
        self.gnuradio.subscribe_parameter('seqnr_missing_recv', '/tmp/gr_seq_missing_recv', np.int32, 1)
        self.gnuradio.subscribe_parameter('seqnr_recv', '/tmp/gr_seq_recv', np.int32, 1)
        self.gnuradio.subscribe_parameter('seqnr_send', '/tmp/gr_seq_send', np.int32, 1)
        self.gnuradio.subscribe_parameter('snr_vect', '/tmp/gr_snr_vect', np.float32, 64)
        self.reset()

    def get_observation_space(self):
        return spaces.Box(low=-100.0, high=40.0, shape=(64, 1), dtype=np.float32)

    def get_action_space(self):
        return spaces.Discrete(8)

    def execute_actions(self, action):
        self.gnuradio.set_parameter('encoding', action)
        self.action = action

    def get_obs(self):
        obs = self.gnuradio.get_parameter('snr_vect')[0]
        return obs[-64:]

    def get_reward(self):
        # get Data of gnuradio
        (missingcounter,) = self.gnuradio.get_parameter('seqnr_missing_recv')
        (senderSeqNr,) = self.gnuradio.get_parameter('seqnr_recv')
        (reveicerSeqNr,) = self.gnuradio.get_parameter('snr_vect')
        (encoding,) = self.gnuradio.get_parameter('encoding')

        missingcounter = missingcounter[-1]
        senderSeqNr = senderSeqNr[-1]
        reveicerSeqNr = reveicerSeqNr[-1]

        # calculate number of send packets in last step and
        # calculate number of received packets in last step and
        # calculate number of lost packets in last step
        totalSend = senderSeqNr - self.lastSendSeqnr
        totalRecv = reveicerSeqNr - self.lastRecvSeqnr
        # detected missing frames at receiver, and difference between sender and receiver
        missingPackets = (missingcounter - self.lastMissingCounter) + (totalSend - totalRecv)

        # calculate effective packet rate -> +1 to avoid division by zero
        reward = (totalSend - missingPackets) / (totalSend + 1) * self.bitrates[encoding]

        self.lastSendSeqnr = senderSeqNr
        self.lastRecvSeqnr = reveicerSeqNr
        self.lastMissingCounter = missingcounter

        return reward

    def get_done(self):
        return False

    def render(self):
        return

    def reset(self):
        # set inital action
        self.execute_actions(0)
        # reset local counter
        missingcounter = self.gnuradio.get_parameter('seqnr_missing_recv')[0]
        senderSeqNr = self.gnuradio.get_parameter('seqnr_recv')[0]
        reveicerSeqNr = self.gnuradio.get_parameter('snr_vect')[0]

        self.lastMissingCounter = missingcounter[-1]
        self.lastSendSeqnr = senderSeqNr[-1]
        self.lastRecvSeqnr = reveicerSeqNr[-1]

    def get_info(self):
        return ""

    def simulate(self):
        # TODO
        return
