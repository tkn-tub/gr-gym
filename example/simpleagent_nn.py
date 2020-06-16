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

model = keras.Sequential()
model.add(keras.layers.Dense(s_size, input_shape=(s_size,), activation='sigmoid'))
model.add(keras.layers.Dense(5, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='softmax'))
model.compile(optimizer=tf.train.AdamOptimizer(0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

epsilon = 1
while True:
    print("--------------------------------------------------------")
    print("new step")
    print("observation:", str(obs))
    action = 0

    if np.random.rand(1) < epsilon:
        action = np.random.randint(a_size)
    else:
        action = np.argmax(model.predict(obs)[0])

    
    print("action:", str(action))
    obs, reward, done, info = env.step(int(action))
    print("reward:", str(reward))
    epsilon *= 0.9
    
    print("Mean:", str(avg))
    print("Dist:", str(num))
    
    if done:
        break
env.close()
