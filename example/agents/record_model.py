import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import xmlrpc.client
import pandas as pd
from tensorflow import keras

filename = 'channel_model.csv'

env = gym.make('grgym:grenv-v0')
obs = env.reset()

gr = xmlrpc.client.ServerProxy("http://" + "localhost" + ":" + str(8080) + "/")

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

cols = []
mycols = []
for i in range(64):
    cols.append('Sc' + str(i))
    mycols.append('Sc' + str(i))
gr.set_f_d(500)
mycols.append('Dist')
mycols.append('Action')
mycols.append('Reward')
df = pd.DataFrame(columns=mycols)
for run in range(5):
    for dist in np.linspace(0, 22, num=22):
        dist = float(dist)
        gr.set_dist(dist)
        obs, reward, done, info = env.step(0)
        for action in range(8):
            obs_new, reward, done, info = env.step(int(action))
            print(obs)
            tmp = pd.DataFrame(data=[obs],
                columns=cols)
            tmp['Dist'] = [dist]
            tmp['Action'] = [action]
            tmp['Reward'] = [reward]
            
            obs = obs_new
            
            print(tmp)
            print(df)
            
            df = pd.concat([df,tmp])
            df.to_csv(filename)

env.close()

print("Fertig")
