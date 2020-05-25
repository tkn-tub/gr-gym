from gym import spaces


class ieee80211codemodscenario:
    def __init(self, gnuradio):
        self.gnuradio = gnuradio
        self.lastSendSeqnr = 0
        self.lastRecvSeqnr = 0
        self.lastMissingCounter = 0
        self.action = 0
        self.bitrates = [
            1.5,    #Mbps BPSK 1/2
            1.25,   #Mbps BPSK 3/4
            3,      #Mbps QPSK 1/2
            4.5,    #Mbps QPSK 3/4
            6,      #Mbps 16QAM 1/2
            9,      #Mbps 16QAM 3/4
            16,     #Mbps 64QAM 2/3
            18      #Mbps 64QAM 3/4
        ]
        
        self.reset()
    
    def get_observation_space(self):
        return spaces.Box(low=-100.0, high=40.0, shape(64,1), dtype=np.float32)

    def get_action_space(self):
        return spaces.Discrete(8)

    def execute_actions(self, action):
        gnuradio.set_encoding(action)
        self.action = action

    def get_obs(self):
        gnuradio.get_snr_vect()[-64:]

    def get_reward(self):
        #get Data of gnuradio
        missingcounter =  gnuradio.get_seqnr_missing_receiver()[-1]
        senderSeqNr = gnuradio.get_seqnr_sender()[-1]
        reveicerSeqNr = gnuradio.get_seqnr_receiver()[-1]
        
        #calculate number of send packets in last step and
        #calculate number of received packets in last step and
        #calculate number of lost packets in last step
        totalSend = senderSeqNr   - self.lastSendSeqnr
        totalRecv = reveicerSeqNr - self.lastRecvSeqnr
        #detected missing frames at receiver, and difference between sender and receiver
        missingPackets = (missingcounter - self.lastMissingCounter) + (totalSend - totalRecv)
        
        #calculate effective packet rate -> +1 to avoid division by zero
        reward = (totalSend - missingPackets) /(totalSend + 1) * self.bitrates[i]
        
        self.lastSendSeqnr = senderSeqNr
        self.lastRecvSeqnr = reveicerSeqNr
        self.lastMissingCounter = missingcounter
        
        return reward
    
    def get_done(self):
        return False
    
    def render(self):
        return
    
    def reset(self):
        #set inital action
        self.execute_action(0)
        #reset local counter
        self.lastSendSeqnr = gnuradio.get_seqnr_sender()[-1]
        self.lastMissingCounter = gnuradio.get_seqnr_missing_receiver()[-1]
    
    def get_info(self):
        return ""
    
    def simulate(self):
        #TODO
        return
