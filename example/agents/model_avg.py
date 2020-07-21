import numpy as np
import matplotlib.pyplot as plt

runsPerEpisode = 20000
epsilonDecay = 0.99998
epsilonStartDecay = 0.99999
epsilonStartPow = 1.53
decayLimit = 0.005

runs = range(runsPerEpisode)
episodes = range(30)

epsilon = 1
epsilon_start = 0.99999999999
for episode in episodes:
    epsilon = epsilon_start
    epsilon_start *= 0.99999
    epsilon_start = pow(epsilon_start, epsilonStartPow)
    y = [epsilon * epsilonDecay ** x for x in runs]
    if(episode % 5 == 0): 
        plt.plot(runs, y, label="episode " + str(episode))
    else:
        plt.plot(runs, y, "b", alpha=0.2)    
plt.xlabel("Steps")
plt.ylabel("Epsilon")
plt.legend()
plt.savefig("epsilon_model.pdf")
plt.savefig("epsilon_model.png")
