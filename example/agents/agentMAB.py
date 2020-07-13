import gym
import numpy as np

env = gym.make('grgym:grenv-v0')
obs = env.reset()

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

a_size = ac_space.n

num = []
avg = []
for i in range(a_size):
    avg.append(0)
    num.append(0)

mean = np.zeros(8)
maxreward = 1

while True:
    print("--------------------------------------------------------")
    print("new step")
    print("observation:", str(obs))
    action = 0

    randval = []
    for i in range(a_size):
        randval.append(np.random.normal(avg[i]/maxreward, 1/(pow(num[i],2) + 1), 1))
    action = np.argmax(randval)
    
    print("action:", str(action))
    obs, reward, done, info = env.step(int(action))
    
    #if reward < 0:
    #    for i in range(2):
    #        obs, reward, done, info = env.step(int(action))
    
    print("reward:", str(reward))
    maxreward = max(reward, maxreward)
    avg[action] = (avg[action] * num[action] + reward) / (num[action] +1)
    num[action] += 1
    
    with open('result.csv','a') as fd:
        fd.write(str(action) + "," + str(reward) + "\n")
    
    print("Mean:", str(avg))
    print("Dist:", str(num))
    
    if done:
        break
env.close()
