'''
gnugym project, TU-Berlin 2020
Sascha Rösler <s.roesler@campus.tu-berlin.de>
Tien Dat Phan <t.phan@campus.tu-berlin.de>
'''
from gym import spaces
import numpy as np
from grgym.envs.gnu_case import gnu_case
from timeit import default_timer as timer


class ieee80211_scenario(gnu_case):
    def __init__(self, gnuradio, args):
        self.gnuradio = gnuradio
        self.args = args
        self.lastSendSeqnr = 0
        self.lastRecvSeqnr = 0
        self.lastMissingCounter = 0
        self.action = 0
        self.nopacketCounter = 0
        self.lastDoneRecvSeqnr = 0
        self.lastObsTime = 0
        self.simcount = 0
        self.low = 0.0
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
        return spaces.Box(low=self.low, high=50.0, shape=(64, 1), dtype=np.float32)

    def get_action_space(self):
        return spaces.Discrete(8)

    def execute_actions(self, action):
        self.gnuradio.set_parameter('encoding', action)
        self.action = action
    
    def _get_reward_state(self, eventbased):
        # get Data of gnuradio
        #missingcounterprev = self.gnuradio.get_parameter_prev('seqnr_missing_recv')[0]
        #senderSeqNrprev = self.gnuradio.get_parameter_prev('seqnr_send')[0]
        #reveicerSeqNrprev = self.gnuradio.get_parameter_prev('seqnr_recv')[0]
        
        if eventbased:
            self.gnuradio.wait_for_value('seqnr_recv')
        
        missingcountertmp = self.gnuradio.get_parameter('seqnr_missing_recv')
        senderSeqNrtmp = self.gnuradio.get_parameter('seqnr_send')
        reveicerSeqNrtmp = self.gnuradio.get_parameter('seqnr_recv')
        
        missingcounter = missingcountertmp[0]
        senderSeqNr = senderSeqNrtmp[0]
        reveicerSeqNr = reveicerSeqNrtmp[0]
        
        missingcounter = missingcounter[-1]
        senderSeqNr = senderSeqNr[-1]
        reveicerSeqNr = reveicerSeqNr[-1]
       
        # calculate number of send packets in last step and
        # calculate number of received packets in last step and
        # calculate number of lost packets in last step
        totalSend = senderSeqNr - self.lastSendSeqnr
        totalRecv = reveicerSeqNr - self.lastRecvSeqnr
        # detected missing frames at receiver, and difference between sender and receiver
        missingPackets = (missingcounter - self.lastMissingCounter)
        
        if(totalSend < -4000):
            totalSend += 4096
        if(totalRecv < -4000):
            totalRecv += 4096
        if(missingPackets < -4000):
            missingPackets += 4096
        
        print("totalSend=" +  str(totalSend) + ", totalRecv=" + str(totalRecv) + ", missingPackets=" + str(missingPackets))

        self.lastSendSeqnr = senderSeqNr
        self.lastRecvSeqnr = reveicerSeqNr
        self.lastMissingCounter = missingcounter
        
        return (totalSend, totalRecv, missingPackets)
    
    def get_obs(self):
        if self.args.eventbased:
            self.gnuradio.wait_for_value('snr_vect')
        (obs, time) = self.gnuradio.get_parameter('snr_vect')
        if(time - self.lastObsTime == 0):
            print("Old DATA!!!!")
            return np.full((1, 64), self.low)[0]
        #reset after simulation
        self.lastObsTime = time
        (totalSend, totalRecv, missingPackets) = self._get_reward_state(False)
        return obs[-64:]

    def get_reward(self):
        encoding = self.gnuradio.get_parameter('encoding')[0]
        (totalSend, totalRecv, missingPackets) = self._get_reward_state(self.args.eventbased)
        # calculate effective packet rate -> +1 to avoid division by zero
        reward = (totalRecv - missingPackets) / (totalSend + 1) * self.bitrates[encoding]

        return float(reward)

    def get_done(self):
        recSeqnr = self.gnuradio.get_parameter('seqnr_recv')[0]
        if recSeqnr == self.lastDoneRecvSeqnr:
            self.nopacketCounter += 1
        else:
            self.nopacketCounter = 0
        self.lastDoneRecvSeqnr = recSeqnr
        if self.nopacketCounter >= self.args.maxRewardLoss:
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
        if self.simcount % self.args.simSteps == 0:
            f_d = np.random.uniform(0,1363)
            dist = np.random.uniform(self.args.simDistMin,self.args.simDistMax)
            print("The distance is " + str(dist) + "dB")
            self.gnuradio.set_parameter("f_d",f_d)
            self.gnuradio.set_parameter("dist",dist)
            self.simcount = 0
        self.simcount += 1
        return
