import gym
import numpy as np
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
from tensorflow import keras

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
model.add(keras.layers.Dense(s_size, input_shape=(s_size,), activation='sigmoid'))
#model.add(keras.layers.Dense(32, activation='relu'))
model.add(keras.layers.Dense(16, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='softmax'))
model.compile(optimizer=tf.train.AdamOptimizer(0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.load_weights("nn_weights.bin")
run = 0
maxreward = 0.0000001

#with open('result_nn.csv','a') as fd:
#    fd.write("Run" +"," + "Episode" + ","+ "Action" + "," + "Reward" + "\n")

while True:
    print("--------------------------------------------------------")
    print("new step")
    
    print("run " + str(run))
    obs = (obs - s_min) / s_range
    obs = np.reshape(obs, [1, s_size])
    
    print("observation:", str(obs))
    action = np.argmax(model.predict(obs)[0])
    
    print("action:", str(action))
    obs_new, reward, done, info = env.step(int(action))
    print("reward:", str(reward), " max reward: ", str(maxreward))
    
    obs = obs_new
    
    maxreward = max(reward, maxreward)
    
    #with open('result_nn.csv','a') as fd:
    #    fd.write(str(run) + "," +str(episode)+ ","+ str(action) + "," + str(reward) + "\n")
    
    run += 1
env.close()
