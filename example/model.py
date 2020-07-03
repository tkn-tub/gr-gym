import numpy as np
import matplotlib.pyplot as plt

runs = range(16)
episodes = range(30)

epsilon = 1
epsilon_start = 0.99999999999
for episode in episodes:
    epsilon = epsilon_start
    epsilon_start *= 0.9999999
    epsilon_start = pow(epsilon_start, 2)
    y = [epsilon * 0.97 ** x for x in runs]
    if(episode % 5 == 0): 
        plt.plot(runs, y, label="episode " + str(episode))
    else:
        plt.plot(runs, y, "b", alpha=0.2)    
plt.legend()
plt.show()

