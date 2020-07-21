import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import xmlrpc.client
import pandas as pd
from tensorflow import keras

filename = 'result_param_obsreward_250ms.csv'

env = gym.make('grgym:grenv-v0')
obs = env.reset()

gr = xmlrpc.client.ServerProxy("http://" + "localhost" + ":" + str(8080) + "/")

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

#with open(filename,'a') as fd:
#    fd.write("Interval" + ","+ "Action" + "," + "Reward," + "Observation,"+ "Observationlong" + "\n")

mycols = ['Interval', 'Action', 'Reward', 'Observation', 'Observationlong']
df = pd.DataFrame(columns=mycols)

#gr.set_dist(20)
#for run in range(5):
#    for f_d in range(0,1363,50):
#        gr.set_f_d(f_d)
#        for action in range(8):
#            obs_new, reward, done, info = env.step(int(action))
#            with open(filename,'a') as fd:
#                fd.write(str(f_d) +"," + "20" + ","+ str(action) + "," + str(reward) + "\n")


interval = 250
for run in range(300):
    #for interval in np.linspace(1,1000,20):
        gr.set_interval(int(interval))
        print("run " + str(run))
        for action in range(8):
            obs, reward, done, info = env.step(int(action))
            #with open(filename,'a') as fd:
            #    fd.write(str(interval) + ","+ str(action) + "," + str(reward) + "\n")
            
            tmp = pd.DataFrame(data=[[int(interval), action, reward, np.average([obs[11], obs[25], obs[39], obs[53]]), np.average(obs)]],
                columns=mycols)
            df = pd.concat([df,tmp])
            df.to_csv(filename)

env.close()

for action in df['Action'].unique():
    tmp = df[df['Action'] == action]
    print(str(action) + ": Observation " + str(np.average(tmp['Observation'])) + "/" + str(np.std(tmp['Observation'])))
    print("\t Observation long: " + str(np.average(tmp['Observationlong'])) + "/" + str(np.std(tmp['Observationlong'])))
    print("\t Reward: " + str(np.average(tmp['Reward'])) + "/" + str(np.std(tmp['Reward'])))

print("Fertig")
