from gym import spaces
import numpy as np
from grgym.envs.gnu_case import gnu_case
from timeit import default_timer as timer


class ieee80211_scenario(gnu_case):
    def __init__(self, gnuradio):
        self.gnuradio = gnuradio
        self.lastSendSeqnr = 0
        self.lastRecvSeqnr = 0
        self.lastMissingCounter = 0
        self.action = 0
        self.nopacketCounter = 0
        self.lastDoneRecvSeqnr = 0
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
        return []

    def get_reward(self):
        # get Data of gnuradio
        #missingcounterprev = self.gnuradio.get_parameter_prev('seqnr_missing_recv')[0]
        #senderSeqNrprev = self.gnuradio.get_parameter_prev('seqnr_send')[0]
        #reveicerSeqNrprev = self.gnuradio.get_parameter_prev('seqnr_recv')[0]
        
        missingcountertmp = self.gnuradio.get_parameter('seqnr_missing_recv')
        senderSeqNrtmp = self.gnuradio.get_parameter('seqnr_send')
        reveicerSeqNrtmp = self.gnuradio.get_parameter('seqnr_recv')
        encoding = self.gnuradio.get_parameter('encoding')[0]
        
        missingcounter = missingcountertmp[0]
        senderSeqNr = senderSeqNrtmp[0]
        reveicerSeqNr = reveicerSeqNrtmp[0]
        
        missingcounter = missingcounter[-1]
        senderSeqNr = senderSeqNr[-1]
        reveicerSeqNr = reveicerSeqNr[-1]
        
        #missingcounterprev = missingcounterprev[-1]
        #senderSeqNrprev = senderSeqNrprev[-1]
        #reveicerSeqNrprev = reveicerSeqNrprev[-1]
        
        #if(senderSeqNr < self.lastSendSeqnr):
        #    senderSeqNr = senderSeqNrprev
        #if(reveicerSeqNr < self.lastRecvSeqnr):
        #    reveicerSeqNr = reveicerSeqNrprev
        #if(missingcounter < self.lastMissingCounter):
        #    missingcounter = missingcounterprev
        
        # calculate number of send packets in last step and
        # calculate number of received packets in last step and
        # calculate number of lost packets in last step
        totalSend = senderSeqNr - self.lastSendSeqnr
        totalRecv = reveicerSeqNr - self.lastRecvSeqnr
        # detected missing frames at receiver, and difference between sender and receiver
        missingPackets = max((missingcounter - self.lastMissingCounter), 0)
        
        # calculate effective packet rate -> +1 to avoid division by zero
        reward = (totalRecv - missingPackets) / (totalSend + 1) * self.bitrates[encoding]
        
        print("Receive:" + str(reveicerSeqNr) + ", last receive" + str(self.lastRecvSeqnr) + "age" + str(reveicerSeqNrtmp[1] - timer()))
        print("Send:" + str(senderSeqNr) + ", last send" + str(self.lastSendSeqnr) + "age" + str(senderSeqNrtmp[1] - timer()))
        print("Missing counter:" + str(missingcounter) + ", last missing" + str(self.lastMissingCounter) + "age" + str(missingcountertmp[1] - timer()))
        print("totalRecv: " + str(totalRecv) + ", missing: " + str(missingPackets) + ", totalSend: " + str(totalSend))

        self.lastSendSeqnr = senderSeqNr
        self.lastRecvSeqnr = reveicerSeqNr
        self.lastMissingCounter = missingcounter

        return float(reward)

    def get_done(self):
        recSeqnr = self.gnuradio.get_parameter('seqnr_recv')[0]
        if recSeqnr == self.lastDoneRecvSeqnr:
            self.nopacketCounter += 1
        else:
            self.nopacketCounter = 0
        self.lastDoneRecvSeqnr = recSeqnr
        if self.nopacketCounter >= 10:
            return True
        return False

    def render(self):
        return

    def reset(self):
        # set inital action
        self.execute_actions(0)
        # reset local counter
        missingcounter = self.gnuradio.get_parameter('seqnr_missing_recv')[0]
        senderSeqNr = self.gnuradio.get_parameter('seqnr_send')[0]
        reveicerSeqNr = self.gnuradio.get_parameter('seqnr_recv')[0]

        self.lastMissingCounter = missingcounter[-1]
        self.lastSendSeqnr = senderSeqNr[-1]
        self.lastRecvSeqnr = reveicerSeqNr[-1]
        
        self.nopacketCounter = 0
        self.lastDoneRecvSeqnr = 0

    def get_info(self):
        return ""

    def simulate(self):
        f_d = np.random.uniform(0,1363)
        dist = np.random.uniform(0,22)

        self.gnuradio.set_parameter("f_d",f_d)
        self.gnuradio.set_parameter("dist",dist)
        return
