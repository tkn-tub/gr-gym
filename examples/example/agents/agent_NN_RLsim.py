import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from random import *

df = pd.read_csv('rssi_sl_raw_long.csv')
logresult = "log_.csv"

# get dataset of best action for each observation (obs and label)
cols = []
for i in range(64):
    cols.append('Sc' + str(i))

df['Run'] = df.apply(lambda row: int(row.name / 8), axis=1)
df = df[df['Reward'] > 0.0]

obs = []
label = []
dist = []
maxrewards = []

for run in df['Run'].unique():
    runData = df[df['Run'] == run]
    myid = runData['Reward'].idxmax()
    myrow = df.loc[myid]
    label.append(myrow['Action'])
    maxrewards.append(myrow['Reward'])
    obs.append(myrow[cols].to_numpy())
    dist.append(myrow['Dist'])
    df.loc[df.Run == run, "Best"] = myrow['Action']

runsPerEpisode = 20000
epsilonDecay = 0.99998
epsilonStartDecay = 0.99999
epsilonStartPow = 1.53
decayLimit = 0.005

class Myenv:
    def __init__(self, df):
        self.df = df
        self.run = 0
        self.runmax = np.max(df['Run'])
    
    def _get_observation(self):
        cols = []
        for i in range(64):
            cols.append('Sc' + str(i))
        error = True
        
        while error:
            tmp = df[df['Run'] == self.run]
            if len(tmp) > 0:
                tmp = tmp.sample()
                error = False
            else:
                self.run +=1
                if self.run > self.runmax:
                    self.run = 0
        return np.array(tmp[cols])[0]
    
    def reset(self):
        return self._get_observation()
    def step(self, action):
        tmp = df[df['Run'] == self.run]
        tmp = tmp[tmp['Action'] == action]
        tmp_reward = np.array(tmp['Reward'])
        if len(tmp_reward) > 0:
            tmp_reward = tmp_reward[0]
        else:
            tmp_reward = 0.0
        self.run += 1
        if self.run > self.runmax:
            self.run = 0
        tmp_obs = self._get_observation()
        return tmp_obs, tmp_reward, False, ""

env = Myenv(df)
obs = env.reset()



a_size = 8
s_size = 64
s_min = 10
s_max = 30
s_range = s_max - s_min

model = keras.Sequential()
model.add(keras.layers.Dense(1, input_shape=(1,), activation='sigmoid'))
model.add(keras.layers.Dense(a_size, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='softmax'))
model.compile(optimizer=tf.optimizers.Adam(0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

epsilon = 1
epsilon_start = 0.99999999999
maxreward = 0.00000000000001

run = 0
episode = 0

with open(logresult,'a') as fd:
    fd.write("Run" +"," + "Episode" + ","+ "Action" + "," + "Reward" + "\n")

while True:
    #print("--------------------------------------------------------")
    #print("new step")
    #print("run " + str(run) + ", epsiode " + str(episode) + " eps = " + str(epsilon))
    action = 0
    #print("Part obs: " + str([obs[11], obs[25], obs[39], obs[53]]))
    #obs = np.average([obs[11], obs[25], obs[39], obs[53]])
    obs = np.average(obs)
    #print("Avg : " + str(obs))
    obs_norm = 2* ((obs - s_min) / s_range -1/2) 
    obs_norm = np.reshape(obs_norm, [1, 1])

    #print("observation:", str(obs_norm))
    if np.random.rand(1) < epsilon:
        action = np.random.randint(a_size)
    else:
        action = np.argmax(model.predict(obs_norm)[0])

    
    #print("action:", str(action))
    obs_new, reward, done, info = env.step(int(action))
    reward = float(reward)
    maxreward = max(reward, maxreward)
    #print("reward:", str(reward))
        
    if obs > 2.0 and reward >= 0:        
        target = np.power((reward / maxreward),1) #* ((4 - np.abs(obs_norm + 2.0)) / (4.0)  + 1)[0][0]
        
        #print("scaled reward: " + str(target))
        
        target_f = model.predict(obs_norm)
        target_f[0][action] = target
        
        if target < 0.1:
            for i in range(action, 8):
                target_f[0][i] = target
        
        #print('New targets '+ str(target_f))
        model.fit(obs_norm, target_f, epochs=1, verbose=0)
    else:
        print("Observation is not in range - No training!")
    
    obs = obs_new
    epsilon *= epsilonDecay
    run += 1
    
    with open(logresult,'a') as fd:
        fd.write(str(run) + "," +str(episode)+ ","+ str(action) + "," + str(reward) + "\n")
    
    if (run % runsPerEpisode) == 0:
        print("New episode" + str(episode+1))
        epsilon = epsilon_start
        epsilon_start *= epsilonStartDecay
        epsilon_start = pow(epsilon_start, epsilonStartPow)
        episode += 1
        model.save_weights('nn_avgsqrt_weights.bin')
    
    if episode > 30 or (epsilon_start < decayLimit and epsilon < decayLimit):
        print("Fertig")
        break

evals = np.linspace(-2,2,100)
actions = []
for elem in evals:
    actions.append(np.argmax(model.predict(evals)[0]))
print(actions)
