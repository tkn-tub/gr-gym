"""
Title: Benchmarking GrGym by testing different IPC mechanisms
Author: Anatolij Zubow

Usage:
    python3 benchmark.py -c bench_pipe.yaml -N 10000 -i 2 -t True
    python3 benchmark.py -c bench_zmq.yaml -N 10000 -i 2 -t True
    python3 benchmark.py -c bench_zmq_remote.yaml -N 10000 -i 2 -t True
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

options, args = parser.parse_args()
print('Benchmarking config file: %s, packet_interval: %s' % (options.config_file, options.packet_interval))

#
# Benchmark GrGym in eventbased mode
#
print('Benchmarking grgym ... ')
N = int(options.N)
trace = options.deep_trace == 'True'
env = gym.make('grgym:grenv-v0', config_file=options.config_file)
# overwrite config file
env.conf.grgym_scenario.packet_interval = int(options.packet_interval)
obs = env.reset()

ac_space = env.action_space
a_size = ac_space.n

action = 0

W = 5
print('Warmup')
for ii in range(W):
    obs, reward, done, info = env.step(int(action))
    #print(obs)

print('Measure N=%d steps' % (N))

if trace:
    ts = np.zeros(N)

step = 0
start = int(round(time.time() * 1000))
for ii in range(N):
    # move to next MCS
    action = (action + 1) % a_size
    if trace:
        s0 = time.time()
    obs, reward, done, info = env.step(int(action))

    if trace:
        s1 = time.time()
        ts[ii] = (s1 - s0) * 1000
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

    with open(options.config_file + '.npy', 'wb') as f:
        np.save(f, ts)

env.close()
