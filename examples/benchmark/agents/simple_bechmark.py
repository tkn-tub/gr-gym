"""
Title: Benchmarking GrGym
Author: Anatolij Zubow

Usage:
python3 simple_bechmark.py -c simple_bench_zmq.yaml -N 10000 -i 1000000 -t False
python3 simple_bechmark.py -c simple_bench_pipe.yaml -N 10000 -i 1000000 -t False

"""

import time
import gym
import optparse
import numpy as np

parser = optparse.OptionParser()

parser.add_option('-c', '--config',
    action="store", dest="config_file",
    help="name of config file", default="bench_pipe.yaml")

parser.add_option('-N', '--num',
    action="store", dest="N",
    help="number of steps", default="1000")

parser.add_option('-i', '--packet_interval',
    action="store", dest="packet_interval",
    help="tx packet interval", default="10")

parser.add_option('-t', '--deep_trace',
    action="store", dest="deep_trace",
    help="activate deep tracing", default=False)

parser.add_option('-o', '--obs_len',
    action="store", dest="obs_len",
    help="obs vector length", default=False)

options, args = parser.parse_args()
print('Benchmarking config file: %s, packet_interval: %s, obs-len: %s' % (options.config_file, options.packet_interval, options.obs_len))

#
# Benchmark GrGym in eventbased mode
#
print('Simple benchmarking grgym ... ')
N = int(options.N)
obs_len = int(options.obs_len)
trace = options.deep_trace == 'True'
env = gym.make('grgym:grenv-v0', config_file=options.config_file)
# overwrite config file
env.conf.grgym_scenario.packet_interval = int(options.packet_interval)
env.conf.grgym_scenario.obs_len = obs_len
obs = env.reset()

ac_space = env.action_space
a_size = ac_space.n

action = 0

W = 0
print('Warmup')
for ii in range(W):
    obs, reward, done, info = env.step(action)
    #print(obs)
    action = action + 1

print('Measure N=%d steps' % (N))

if trace:
    print('Do deep tracing')
    ts = np.zeros(N)
    osv = np.zeros(N)

action = 0
step = 0
start = int(round(time.time() * 1000))
for ii in range(N):
    # move to next MCS
    action = action + 1
    if trace:
        s0 = time.time()
    obs, reward, done, info = env.step(int(action))
    #print(time.time())
    #print(obs.shape[0])
    #print(obs)
    if trace:
        s1 = time.time()
        ts[ii] = (s1 - s0) * 1000
        osv[ii] = obs.shape[0]
    step = step + 1

end = int(round(time.time() * 1000))

delta = (end - start) / 1000.0
steps_per_second = 1.0 / (delta / N)

print('Done')
print('Start: %d, end: %d, delta=: %.4f [sec]' % (start, end, delta))
print('Steps per second: %.4f' % (steps_per_second))

if trace:
    print('statics of results')
    print('* num of valid data: {0}'.format(len(ts)))
    print('* min: {0:.6f} ms'.format(min(ts)))
    print('* max: {0:.6f} ms'.format(max(ts)))
    print('* mean: {0:.6f} ms'.format(np.mean(ts)))
    print('* median: {0:.6f} ms'.format(np.median(ts)))
    print('* std: {0:.6f} ms'.format(np.std(ts)))
    print('* obs mean: {0:.6f}'.format(np.median(osv)))

env.close()
