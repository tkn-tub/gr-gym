from gym import spaces


class ieee80211codemodscenario:
    def __init(self, gnuradio):
        self.gnuradio = gnuradio
        self.lastSendSeqnr = 0
        self.lastMissingCounter = 0
    
    def get_observation_space(self):
        return spaces.Box(low=-100.0, high=40.0, shape(64,1), dtype=np.float32)

    def get_action_space(self):
        return spaces.Discrete(8)

    def execute_action(self, action):
        gnuradio.set_encoding(action)

    def get_observation(self):
        gnuradio.get_snr_vect()[-64:]

    def get_reward(self):
        #get Data of gnuradio
        missingcounter =  gnuradio.get_seqnr_missing_receiver()[-1]
        senderSeqNr = gnuradio.get_seqnr_sender()[-1]
        reveicerSeqNr = gnuradio.get_seqnr_receiver()[-1]
        
        #calculate number of send packets in last step and
        #calculate number of lost pacehts in last step
        totalSend = senderSeqNr - self.lastSendSeqnr
        #detected missing frames at receiver, and difference between sender and receiver
        missingPackets = (missingcounter - self.lastMissingCounter) + (senderSeqNr - reveicerSeqNr)
        
        #calculate percentage as reward -> +1 to avoid division by zero
        reward = (totalSend - missingPackets) /(totalSend + 1)
        
        self.lastSendSeqnr = senderSeqNr
        self.lastMissingCounter = missingcounter
        
        return reward
    
    def get_gameover(self):
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
