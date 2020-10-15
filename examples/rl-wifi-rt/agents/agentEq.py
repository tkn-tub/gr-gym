"""
Title: Non-learning agent. Just select the MCSs available in round-robin.
Author: Anatolij Zubow
Date created: 2020/10/1
"""

import os
import gym
import numpy as np
from datetime import datetime
import optparse

parser = optparse.OptionParser()

parser.add_option('-c', '--config',
    action="store", dest="config_file",
    help="name of config file", default="config.yaml")

options, args = parser.parse_args()
print('Using config file: %s' % (options.config_file))

#
# Probe the MCSs in RR
#

env = gym.make('grgym:grenv-v0', config_file=options.config_file)
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

num = []
avg = []
for i in range(a_size):
    avg.append(0)
    num.append(0)

sc_min = 6
sc_dc = 32
sc_max = 59

# start with lowest MCS
action = 0

step = 1

dir = './results/agent_eq/'
if not os.path.exists(dir):
    os.makedirs(dir)
logfile = dir + 'raw.csv'
with open(logfile, 'w') as fd:
    fd.write("\n")

while True:
    print("--------------------------------------------------------")
    print("%s: step: %d" % (datetime.now().time(), step))

    # remove null carriers
    obsl = obs[sc_min:sc_dc]
    obsr = obs[sc_dc+1:sc_max]

    obs = []
    obs.extend(obsl)
    obs.extend(obsr)

    avg_obs = np.mean(obs)
    obs_db = 10.0 * np.log10(avg_obs)

    print("# %s: %d observation %.2f %.2f dB" % (datetime.now().time(), step, avg_obs, obs_db))

    # move to next MCS
    action = (action + 1) % a_size

    print("# %s: %d action: %d" % (datetime.now().time(), step, action))
    obs, reward, done, info = env.step(int(action))

    print("# %s: %d reward: %.2f done: %s" % (datetime.now().time(), step, reward, str(done)))
    avg[action] = (avg[action] * num[action] + reward) / (num[action] +1)
    num[action] += 1

    # save old observation
    with open(logfile, 'a') as fd:
        fd.write(str(avg_obs) + "," + str(action) + "," + str(reward) + "," + str(obs_db) + "\n")

    print("avg reward:", str(avg))
    print("num probes:", str(num))

    step = step + 1

env.close()
