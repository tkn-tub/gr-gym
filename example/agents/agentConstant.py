import gym
import numpy as np
import time 

env = gym.make('grgym:grenv-v0')
obs = env.reset()

ac_space = env.action_space
ob_space = env.observation_space
print("Observation space: ", ob_space,  ob_space.dtype)
print("Action space: ", ac_space, ac_space.n)

a_size = ac_space.n


while True:
    print("--------------------------------------------------------")
    print("new step")
    print("observation:", str(obs))
    action = 7
    
    print("action:", str(action))
    obs, reward, done, info = env.step(int(action))
    print("reward:", str(reward))
    
env.close()
