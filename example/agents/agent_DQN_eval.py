import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
from tensorflow import keras

logresult = 'agentdata/result_nn_avg.csv'

env = gym.make('grgym:grenv-v0')
obs = env.reset()

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

a_size = ac_space.n
s_size = ob_space.shape[0]
s_min = ob_space.low[0]
s_max = ob_space.high[0]
s_range = s_max - s_min

model = keras.Sequential()
model.add(keras.layers.Dense(1, input_shape=(1,), activation='sigmoid'))
model.add(keras.layers.Dense(a_size, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='softmax'))
model.compile(optimizer=tf.train.AdamOptimizer(0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.load_weights('agentdata/nn_avgsqrt_weights.bin')

while True:
    print("--------------------------------------------------------")
    print("new step")
    
    obs = np.average([obs[11], obs[25], obs[39], obs[53]])
    print("Avg : " + str(obs))
    obs = 2* 2* ((obs - s_min) / s_range -1/2) 
    obs = np.reshape(obs, [1, 1])

    print("observation:", str(obs))
    action = np.argmax(model.predict(obs)[0])

    
    print("action:", str(action))
    obs, reward, done, info = env.step(int(action))
    print("reward:", str(reward))
    
env.close()
