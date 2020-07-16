import numpy as np
import gym
from pilco.models import PILCO
from pilco.controllers import RbfController, LinearController
from pilco.rewards import ExponentialReward
import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
np.random.seed(0)

from utils import rollout, policy


class myPendulum():
    def __init__(self):
        self.env = gym.make('grgym:grenv-v0')
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        obs = np.average(obs)
        return [obs, reward, done, info]

    def reset(self):
        x_new =  np.average(self.env.reset())
        return x_new

    def render(self):
        self.env.render()

        
env = myPendulum()

# Settings, are explained in the rest of the notebook
SUBS=3 # subsampling rate
T = 2 # number of timesteps (for planning, training and testing here)
J = 3 # rollouts before optimisation starts

max_action=7.0 # used by the controller, but really defined by the environment

# Reward function parameters
target = np.array([1.0, 0.0])
weights = np.diag([2.0, 2.0])

# Environment defined
m_init = np.reshape([-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], (10,2))
S_init = np.diag([0.01, 0.01, 0.01])

# Random rollouts
X,Y, _, _ = rollout(env, None, timesteps=T, verbose=True, random=True, SUBS=SUBS, render=False)
print("Shape Y " + str(Y.shape))
print("Y " + str(Y))
print("Shape X " + str(X.shape))
print("X " + str(X))

for i in range(1,J):
    X_, Y_, _, _ = rollout(env, None, timesteps=T, verbose=True, random=True, SUBS=SUBS, render=False)
    X = np.vstack((X, X_))
    Y = np.vstack((Y, Y_))

print("Shape Y " + str(Y.shape[1]))
print("Y " + str(Y))
print("Shape X " + str(X.shape[1]))
print("X " + str(X))

state_dim = Y.shape[1]
control_dim = 0 #X.shape[1] - state_dim
Y = Y.reshape(Y.size,1)
controller = RbfController(state_dim=state_dim, control_dim=control_dim, num_basis_functions=10, max_action=max_action)
R = ExponentialReward(state_dim=state_dim, t=target, W=weights)
pilco = PILCO((X, Y), controller=controller, horizon=T, reward=R, m_init=m_init, S_init=S_init)

# Training model and policy
pilco.optimize_models(maxiter=100)
pilco.optimize_policy(maxiter=20)

# Rollout using the pilco controller
X_new, Y_new, _, _ = rollout(env, pilco, timesteps=T, SUBS=SUBS, render=False)

for i,m in enumerate(pilco.mgpr.models):
    print("Model " + str(i))
    y_pred_test, var_pred_test = m.predict_y(X_new)
    print("X:" + str(X_new))
    print("y_pred_test:" + str(y_pred_test))
