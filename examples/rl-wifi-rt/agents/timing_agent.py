import gym
import numpy as np
#import tensorflow as tf
#import tensorflow.contrib.slim as slim
#import numpy as np
import xmlrpc.client
import pandas as pd
#from tensorflow import keras
from timeit import default_timer as timer

filename = 'timing.csv'

env = gym.make('grgym:grenv-v0')
obs = env.reset()

gr = xmlrpc.client.ServerProxy("http://" + "localhost" + ":" + str(8080) + "/")

mycols = []
mycols.append('Interval')
mycols.append('Timing')
df = pd.DataFrame(columns=mycols)
for run in range(1):
    #for dist in range(0,22,0.1):
    gr.set_dist(5.0)
    for interval in np.linspace(1000, 1, num=50):
        print("Interval " + str(interval))
        interval = int(interval)
        gr.set_interval(interval)
        env.set_interval(interval)
        
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

env.close()

print("Fertig")
