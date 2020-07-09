import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import xmlrpc.client
from tensorflow import keras

filename = 'result_param_dist_25_gnc.csv'

env = gym.make('grgym:grenv-v0')
obs = env.reset()

gr = xmlrpc.client.ServerProxy("http://" + "localhost" + ":" + str(8080) + "/")

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

with open(filename,'a') as fd:
    fd.write("f_d" +"," + "dist" + ","+ "Action" + "," + "Reward" + "\n")

#gr.set_dist(20)
#for run in range(5):
#    for f_d in range(0,1363,50):
#        gr.set_f_d(f_d)
#        for action in range(8):
#            obs_new, reward, done, info = env.step(int(action))
#            with open(filename,'a') as fd:
#                fd.write(str(f_d) +"," + "20" + ","+ str(action) + "," + str(reward) + "\n")

gr.set_f_d(500)
for run in range(5):
    for dist in range(0,30,2):
        gr.set_dist(dist)
        for action in range(8):
            obs_new, reward, done, info = env.step(int(action))
            with open(filename,'a') as fd:
                fd.write(str(500) +"," + str(dist) + ","+ str(action) + "," + str(reward) + "\n")

env.close()

print("Fertig")
