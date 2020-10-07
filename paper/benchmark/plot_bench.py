import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

names = []
data = []

with open('data/bench_pipe.yaml.npy', 'rb') as f:
    pipe = np.load(f)
    names.extend(['local FPIPE'] * len(pipe))
    data.extend(pipe)

with open('data/bench_zmq.yaml.npy', 'rb') as f:
    zmq = np.load(f)
    names.extend(['local ZMQ'] * len(zmq))
    data.extend(zmq)

with open('data/bench_zmq_fritz.yaml.npy', 'rb') as f:
    zmqr = np.load(f)
    names.extend(['remote ZMQ (100 Mbit/s)'] * len(zmqr))
    data.extend(zmqr)

# show median values
print('Median step duration: file=%.3f, loczmq=%.3f, remzmq=%.3f' % (np.median(pipe), np.median(zmq), np.median(zmqr)))

dict = {'name': names, 'value' : data}

df = pd.DataFrame(dict)

fig = plt.figure(figsize=(7, 4))
sns.violinplot(x=df.name, y=df.value)
#sns.violinplot(data)
plt.grid()
#plt.title('Benchmark')
plt.ylabel('Step duration [ms]')
plt.xlabel('IPC technology observation collection')
plt.savefig('../figs/benchmark.pdf')
plt.show()