import matplotlib
import numpy as np
import csv
from matplotlib import pyplot as plt
import optparse

parser = optparse.OptionParser()

parser.add_option('-d', '--dir',
    action="store", dest="dir",
    help="dir path", default="./results/agent_ac")

parser.add_option('-l', '--last',
    action="store", dest="last",
    help="last n items", default="-1")

options, args = parser.parse_args()
last_n = int(options.last)
dir = options.dir

print('Path: %s' % (dir))
print('Show last n items: %d' % (last_n))

logfile = dir + '/raw.csv'

fig2 = plt.figure(figsize=(10, 5))

x = []
y = []
with open(logfile, 'r') as fd:
    reader = csv.reader(fd)
    for row in reader:
        #print(row)
        if len(row) > 0:
            x.append(float(row[0]))
            y.append(float(row[2]))

if last_n == -1:
    plt.scatter(x, y)
    last_n = len(x)
else:
    plt.scatter(x[-last_n:], y[-last_n:])

plt.xlabel("obs")
plt.ylabel("reward")
plt.title("obs vs. reward: N=" + str(last_n) )
plt.grid()
plt.ylim((-1, 30))
plt.show()
