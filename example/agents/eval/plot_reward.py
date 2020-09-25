import matplotlib
import numpy as np
import csv
from matplotlib import pyplot as plt
import optparse

parser = optparse.OptionParser()

parser.add_option('-d', '--dir',
    action="store", dest="dir",
    help="dir path", default="./results/agent_ac")

options, args = parser.parse_args()
dir = options.dir

print('Path: %s' % (dir))

logfile = dir + '/running_reward.csv'

fig2 = plt.figure(figsize=(10, 5))

episode_offset = 1
rewards_smoothed = []
with open(logfile, 'r') as fd:
    reader = csv.reader(fd)
    for row in reader:
        if len(row) > 0:
            if int(row[2]) % episode_offset == 0:
                rewards_smoothed.append(float(row[0]))

plt.plot(rewards_smoothed)
plt.xlabel("Episode")
plt.ylabel("Episode Reward (Smoothed)")
plt.title("Episode Reward over Time")
plt.grid()
plt.show()
