import random
import gym
import math
import pickle
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

def float_to_bin_vec(v, no_bits=10):
    scale = np.power(2, no_bits-1)

    # convert to binary vector
    y = list(bin(round(v * scale))[2:])
    y = [int(v) for v in y]
    y2 = list(np.zeros(no_bits - len(y)))
    y2.extend(y)

    return np.reshape(y2, [1, no_bits])

def bin_vec_to_float(b, no_bits=10):
    p = [np.power(2, x) for x in range(no_bits-1, -1, -1)]
    scale = np.power(2, no_bits-1)
    y = sum(b[0] * p) / scale

    return y

class DQNARQSolver():
    def __init__(self, just_replay=False, n_episodes=1000, max_env_steps=100, gamma=1.0, epsilon=1.0, epsilon_min=0.01, epsilon_log_decay=0.999999, alpha=0.01, alpha_decay=0.01, batch_size=256, quiet=False):
        self.memory = deque(maxlen=100000)
        self.env = gym.make('grgym:grenv-v0')
        self.just_replay = just_replay
        self.n_win_ticks = 100
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_log_decay
        self.alpha = alpha
        self.alpha_decay = alpha_decay
        self.n_episodes = n_episodes
        self.batch_size = batch_size
        self.quiet = quiet
        self.max_env_steps = max_env_steps

        self.logfile = './rl/agentRLng.csv'
        with open(self.logfile, 'w') as fd:
            fd.write("\n")

        self.model_path = './rl/gnugym_rl_wifi/'

        # quantization
        self.no_bits = 6 #10
        print("No. of quantization bits: %d" % (self.no_bits))

        self.obs_high = 35
        self.obs_low = 8

        # Init model
        self.model = Sequential()
        self.model.add(Dense(self.no_bits, input_dim=self.no_bits, activation='relu'))
        self.model.add(Dense(128, activation='relu'))
        #self.model.add(Dense(32, activation='relu'))
        self.model.add(Dense(self.env.action_space.n, activation='softmax'))
        self.model.compile(loss='mse', optimizer=Adam(lr=self.alpha, decay=self.alpha_decay))

        print(self.model.summary())

        self.av_bitrates = [
            3,  # Mbps BPSK 1/2
            4.5,  # Mbps BPSK 3/4
            6,  # Mbps QPSK 1/2
            9,  # Mbps QPSK 3/4
            12,  # Mbps 16QAM 1/2
            18,  # Mbps 16QAM 3/4
            24,  # Mbps 64QAM 2/3
            27  # Mbps 64QAM 3/4
        ]
        np.seterr(invalid='raise')
        self.save_mem = True
        self.mem_fname = './rl/agentRLng.p'
        self.take_future_reward = False

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if self.save_mem:
            pickle.dump(self.memory, open(self.mem_fname, "wb"))

    def choose_action(self, state, epsilon):
        #return self.env.action_space.sample() if (np.random.random() <= epsilon) else np.argmax(self.model.predict(state))
        valid_mcs = [3, 4, 5, 7]

        while True:
            action = self.env.action_space.sample() if (np.random.random() <= epsilon) else np.argmax(self.model.predict(state))
            if action in valid_mcs:
                return action

    def get_epsilon(self, t):
        e_val = max(self.epsilon_min, min(self.epsilon, 1.0 - math.log10((t + 1) * self.epsilon_decay)))
        print("Curr eps: %.4f" % e_val)
        return e_val

    def preprocess_state(self, state):
        sc_min = 6
        sc_dc = 32
        sc_max = 59

        # remove null carriers
        obsl = state[sc_min:sc_dc]
        obsr = state[sc_dc + 1:sc_max]

        obs = []
        obs.extend(obsl)
        obs.extend(obsr)

        avg_obs = np.mean(obs)
        if avg_obs > self.obs_high or avg_obs < self.obs_low:
            print("WARNING: observation out of range! %.2f" % (avg_obs))
            avg_obs = max(avg_obs, self.obs_low)
            avg_obs = min(avg_obs, self.obs_high)

        x = (avg_obs - self.obs_low) / (self.obs_high - self.obs_low)
        return float_to_bin_vec(x, self.no_bits)

    def replay(self, batch_size):
        print("replaying ... mem sz: %d, batch sz: %d" % (len(self.memory), batch_size))
        x_batch, y_batch = [], []
        minibatch = random.sample(
            self.memory, min(len(self.memory), batch_size))
        for state, action, reward, next_state, done in minibatch:
            y_target = self.model.predict(state)
            for a in range(8):
                #if a not in valid_mcs:
                y_target[0][a] = 0

            if self.take_future_reward:
                y_target[0][action] = reward if done else reward + self.gamma * np.max(self.model.predict(next_state)[0])
            else:
                y_target[0][action] = reward
            x_batch.append(state[0])
            y_batch.append(y_target[0])

        self.model.fit(np.array(x_batch), np.array(y_batch), batch_size=len(x_batch), verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def run(self):
        scores = deque(maxlen=100)

        if self.just_replay:
            self.memory = pickle.load(open(self.mem_fname, "rb"))

        for e in range(self.n_episodes):

            if self.just_replay:
                print('nop')
            else:
                state = self.preprocess_state(self.env.reset())

                s = 0
                done = False
                i = 0

                e_val = self.get_epsilon(e)
                while not done:
                    action = self.choose_action(state, e_val)

                    next_state, reward, done, _ = self.env.step(action)
                    next_state = self.preprocess_state(next_state)

                    state_norm = bin_vec_to_float(state, self.no_bits)
                    next_state_norm = bin_vec_to_float(next_state, self.no_bits)
                    #print("%d.%d: observation: %.2f / %.2f, action: %d, reward: %.2f" % (e, s, state_norm, next_state_norm, action, reward))

                    with open(self.logfile, 'a') as fd:
                        fd.write(str(state_norm) + "," + str(action) + "," + str(reward) + "\n")

                    self.remember(state, action, reward, next_state, done)
                    state = next_state
                    i += reward
                    s += 1

                    if s > self.max_env_steps:
                        #print("Max. no. of steps reached. %d" % (s))
                        break

                #print('sum-reward last episod: %d' % (i))
                scores.append(i)
                mean_score = np.mean(scores)

                self.model.save(self.model_path)

                if not self.quiet:
                    print('[Episode {}] - Mean reward last episodes was {}.'.format(e, mean_score))

            self.replay(self.batch_size)

        if not self.quiet: print('Did not solve after {} episodes 😞'.format(e))
        return e

if __name__ == '__main__':
    agent = DQNARQSolver(just_replay=False)
    agent.run()
