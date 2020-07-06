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
model.add(keras.layers.Dense(32, activation='relu'))
model.add(keras.layers.Dense(16, activation='relu'))
model.add(keras.layers.Dense(a_size, activation='softmax'))
model.compile(optimizer=tf.train.AdamOptimizer(0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

epsilon = 1
epsilon_start = 0.99999999999
maxreward = 0.00000000000001
run = 0
episode = 0

with open('result_nn.csv','a') as fd:
    fd.write("Run" +"," + "Episode" + ","+ "Action" + "," + "Reward" + "\n")

while True:
    print("--------------------------------------------------------")
    print("new step")
    print("observation:", str(obs))
    print("run " + str(run) + ", epsiode " + str(episode) + " eps = " + str(epsilon))
    action = 0
    obs = np.reshape(obs, [1, s_size])

    if np.random.rand(1) < epsilon:
        action = np.random.randint(a_size)
    else:
        action = np.argmax(model.predict(obs)[0])

    
    print("action:", str(action))
    obs_new, reward, done, info = env.step(int(action))
    print("reward:", str(reward), " max reward: ", str(maxreward))
    
    maxreward = max(reward, maxreward)
    
    target = (reward)/maxreward
    
    target_f = model.predict(obs)
    target_f[0][action] = target
    print("agent new learning" + str(target_f))
    model.fit(obs, target_f, epochs=1, verbose=0)
    
    with open('result_nn.csv','a') as fd:
        fd.write(str(run) + "," +str(episode)+ ","+ str(action) + "," + str(reward) + "\n")
    
    obs = obs_new
    epsilon *= 0.97
    run += 1
    
    if (run % 25) == 0:
        epsilon = epsilon_start
        epsilon_start *= 0.9999999
        epsilon_start = pow(epsilon_start, 2)
        episode += 1
        model.save_weights('nn_weights.bin')
    
    #print("Mean:", str(avg))
    #print("Dist:", str(num))
    
    if done or episode > 30 or (epsilon_start < 0.01 and epsilon < 0.01):
        break
env.close()
