import time
import gym
import optparse

#
# Benchmark GrGym in eventbased mode
#
N = 1000
config_file = 'bench.yaml'
print('Using config file: %s' % (config_file))
env = gym.make('grgym:grenv-v0', config_file=config_file)
obs = env.reset()

ac_space = env.action_space
a_size = ac_space.n

action = 0

W = 10
print('Warmup')
for ii in range(W):
    obs, reward, done, info = env.step(int(action))

print('Measure N=%d steps' % (N))

step = 0
start = int(round(time.time() * 1000))
for ii in range(N):
    # move to next MCS
    action = (action + 1) % a_size
    obs, reward, done, info = env.step(int(action))
    step = step + 1

end = int(round(time.time() * 1000))

delta = (end - start) / 1000.0
steps_per_second = 1.0 / (delta / N)

print('Done')
print('Start: %d, end: %d, delta=: %.4f [sec]' % (start, end, delta))
print('Steps per second: %.4f' % (steps_per_second))

env.close()
