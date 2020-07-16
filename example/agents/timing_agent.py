import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import xmlrpc.client
import pandas as pd
#from tensorflow import keras
from timeit import default_timer as timer

filename = 'timing.csv'

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
mycols = []
mycols.append('Interval')
mycols.append('Timing')
df = pd.DataFrame(columns=mycols)
for run in range(1):
    #for dist in range(0,22,0.1):
    gr.set_dist(5.0)
    for interval in np.linspace(1000, 1, num=50):
        interval = int(interval)
        gr.set_interval(interval)
        #env.set_interval(interval)
        
        for i in range(10):
            start = timer()
            obs_new, reward, done, info = env.step(int(0))
            stop = timer()
            print(start)
            print(stop)
            print(stop -start)
            tmp = pd.DataFrame(data=[[int(interval), (stop-start)]],
                columns=mycols)
            df = pd.concat([df,tmp])
df.to_csv(filename)
'''
        for action in range(8):
            
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
            
            #with open(filename,'a') as fd:
            #    fd.write(str(dist) + ","+ str(obs_new) + "\n")
'''
env.close()

print("Fertig")
