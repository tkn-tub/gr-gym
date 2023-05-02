import gym
import numpy as np
import tensorflow as tf
import numpy as np
from tensorflow import keras

logresult = 'agentdata/result_nn_avgsqrt.csv'
runsPerEpisode = 1000
epsilonDecay = 0.9993
epsilonStartDecay = 0.99999
epsilonStartPow = 1.5
decayLimit = 0.005

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

epsilon = 1
epsilon_start = 0.99999999999
maxreward = 0.00000000000001 

run = 0
episode = 0

with open(logresult,'a') as fd:
    fd.write("Run" +"," + "Episode" + ","+ "Action" + "," + "Reward" + "\n")

while True:
    print("--------------------------------------------------------")
    print("new step")
    print("run " + str(run) + ", epsiode " + str(episode) + " eps = " + str(epsilon))
    action = 0
    #print("Part obs: " + str([obs[11], obs[25], obs[39], obs[53]]))
    #obs = np.average([obs[11], obs[25], obs[39], obs[53]])
    obs = np.average(obs)
    print("Avg : " + str(obs))
    obs_norm = 2* 2* ((obs - s_min) / s_range -1/2) 
    obs_norm = np.reshape(obs_norm, [1, 1])

    print("observation:", str(obs_norm))
    if np.random.rand(1) < epsilon:
        action = np.random.randint(a_size)
    else:
        action = np.argmax(model.predict(obs_norm)[0])

    
    print("action:", str(action))
    obs_new, reward, done, info = env.step(int(action))
    print("reward:", str(reward), " max reward: ", str(maxreward))
    
    if obs > 2.0 and reward >= 0:
        maxreward = max(reward, maxreward)
        
        target = np.power((reward)/maxreward,1/2) * ((4 - np.abs(obs_norm + 2.0)) / (4.0)  + 1) 
        
        print("scaled reward: " + str(target))
        
        target_f = model.predict(obs_norm)
        target_f[0][action] = target
        
        if target < 0.1:
            for i in range(action, 8):
                target_f[0][i] = target
        
        print('New targets '+ str(target_f))
        model.fit(obs_norm, target_f, epochs=1, verbose=0)
    else:
        print("Observation is not in range - No training!")
    with open(logresult,'a') as fd:
        fd.write(str(run) + "," +str(episode)+ ","+ str(action) + "," + str(reward) + "\n")
    
    obs = obs_new
    epsilon *= epsilonDecay
    run += 1
    
    if (run % runsPerEpisode) == 0:
        epsilon = epsilon_start
        epsilon_start *= epsilonStartDecay
        epsilon_start = pow(epsilon_start, epsilonStartPow)
        episode += 1
        model.save_weights('agentdata/nn_avgsqrt_weights.bin')
    
    if done:
        run = 0
        epsilon = 1
        epsilon_start = 0.99999999999
    if episode > 30 or (epsilon_start < decayLimit and epsilon < decayLimit):
        print("Fertig")
        break

env.close()
