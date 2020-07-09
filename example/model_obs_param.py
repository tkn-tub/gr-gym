import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import xmlrpc.client
import pandas as pd
from tensorflow import keras

filename = 'result_obs_dist_25_gnc.csv'

env = gym.make('grgym:grenv-v0')
obs = env.reset()

gr = xmlrpc.client.ServerProxy("http://" + "localhost" + ":" + str(8080) + "/")

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

#with open(filename,'a') as fd:
#    fd.write("f_d" +"," + "dist" + ","+ "Action" + "," + "Reward" + "\n")

#gr.set_dist(20)
#for run in range(5):
#    for f_d in range(0,1363,50):
#        gr.set_f_d(f_d)
#        for action in range(8):
#            obs_new, reward, done, info = env.step(int(action))
#            with open(filename,'a') as fd:
#                fd.write(str(f_d) +"," + "20" + ","+ str(action) + "," + str(reward) + "\n")

cols = []
mycols = []
for i in range(64):
    cols.append('Sc' + str(i))
    mycols.append('Sc' + str(i))
gr.set_f_d(500)
mycols.append('Dist')
df = pd.DataFrame(columns=mycols)
for run in range(5):
    for dist in range(0,30,2):
        gr.set_dist(dist)
        for action in range(8):
            obs_new, reward, done, info = env.step(int(action))
            print(obs_new)
            tmp = pd.DataFrame(data=[obs_new],
                columns=cols)
            tmp['Dist'] = [dist]
            
            print(tmp)
            print(df)
            
            df = pd.concat([df,tmp])
            df.to_csv(filename)
            
            #with open(filename,'a') as fd:
            #    fd.write(str(dist) + ","+ str(obs_new) + "\n")

env.close()

print("Fertig")
