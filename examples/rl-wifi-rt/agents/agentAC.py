"""
Title: Actor Critic Method for MCS Selection in IEEE 802.11p
Author: Anatolij Zubow
Date created: 2020/09/24
Description: Implement Actor Critic Method in GnuGym environment with IEEE 802.11p MCS selection scenario.
"""


import os
import gym
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

debug = False

# for faster learning we normalize the observation space
obs_low = 14
obs_high = 35

# Configuration parameters for the whole setup
seed = 42
gamma = 0 #0.99  # Discount factor for past rewards; must be zero for MCS selection
max_steps_per_episode = 100
env = gym.make('grgym:grenv-v0')  # Create the environment
env.seed(seed)
eps = np.finfo(np.float32).eps.item()  # Smallest number such that 1.0 + eps != 1.0

# logging for later processing
dir = './results/agent_ac/'
if not os.path.exists(dir):
    os.makedirs(dir)
logfile = dir + 'running_reward.csv'
with open(logfile, 'w') as fd:
    fd.write("\n")
logfile_raw = dir + 'raw.csv'
with open(logfile_raw, 'w') as fd:
    fd.write("\n")

"""
## Implement Actor Critic network

This network learns two functions:

1. Actor: This takes as input the state of our environment and returns a
probability value for each action in its action space.
2. Critic: This takes as input the state of our environment and returns
an estimate of total rewards in the future.

In our implementation, they share the initial layer.
"""

'''
    Normalize observation (per OFDM subcarrier RSSI) to [0, 1] interval
    Just remove the DC & null carriers and compute the mean value which is
    fine in AWGN channel.
'''
def preprocess_state(state):
    sc_min = 6
    sc_dc = 32
    sc_max = 59

    # remove null/DC subcarriers
    obsl = state[sc_min:sc_dc]
    obsr = state[sc_dc + 1:sc_max]

    obs = []
    obs.extend(obsl)
    obs.extend(obsr)
    avg_obs = np.mean(obs)

    if avg_obs < obs_low:
        print('Warning: obs too low %.2f' % (avg_obs))
        avg_obs = obs_low

    if avg_obs > obs_high:
        print('Warning: obs too high %.2f' % (avg_obs))
        avg_obs = obs_high

    x = (avg_obs - obs_low) / (obs_high - obs_low)
    
    return x


# NN configuration
num_inputs = 1
num_actions = env.action_space.n
num_hidden = 128

inputs = layers.Input(shape=(num_inputs,))
common = layers.Dense(num_hidden, activation="relu")(inputs)
action = layers.Dense(num_actions, activation="softmax")(common)
critic = layers.Dense(1)(common)

model = keras.Model(inputs=inputs, outputs=[action, critic])
print(model.summary())

"""
## Train
"""

opt_learn_rate = 0.1 #0.01
optimizer = keras.optimizers.Adam(learning_rate=opt_learn_rate)
huber_loss = keras.losses.Huber()
action_probs_history = []
critic_value_history = []
rewards_history = []
running_reward = 0
episode_count = 0

while True:  # Run until solved
    state = preprocess_state(env.reset())
    episode_reward = 0
    with tf.GradientTape() as tape:

        reward_in_epoch = 0
        actions_in_epoch = dict.fromkeys(range(num_actions), 0)
        for timestep in range(1, max_steps_per_episode):
            # env.render(); Adding this line would show the attempts
            # of the agent in a pop up window.
            last_state = state
            state = tf.convert_to_tensor(state)
            state = tf.expand_dims(state, 0)

            # Predict action probabilities and estimated future rewards
            # from environment state
            action_probs, critic_value = model(state)
            critic_value_history.append(critic_value[0, 0])

            # Sample action from action probability distribution
            p_a = np.squeeze(action_probs)
            action = np.random.choice(num_actions, p = p_a)

            action_probs_history.append(tf.math.log(action_probs[0, action]))
            actions_in_epoch[action] += 1

            # Apply the sampled action in our environment
            state, reward, done, _ = env.step(action)
            state = preprocess_state(state)

            if debug:
                print("%d: next state: %.2f, action: %d, reward: %.2f" % (timestep, state, action, reward))

            with open(logfile_raw, 'a') as fd:
                fd.write(str(last_state) + "," + str(action) + "," + str(reward) + "\n")

            rewards_history.append(reward)
            episode_reward += reward
            reward_in_epoch += reward

            if done:
                break

        print('log:avg reward_in_epoch=%.2f' % (reward_in_epoch / max_steps_per_episode))
        print(actions_in_epoch)

        # Update running reward to check condition for solving
        running_reward = 0.05 * episode_reward + (1 - 0.05) * running_reward

        # Calculate expected value from rewards
        # - At each timestep what was the total reward received after that timestep
        # - Rewards in the past are discounted by multiplying them with gamma
        # - These are the labels for our critic
        returns = []
        discounted_sum = 0
        for r in rewards_history[::-1]:
            discounted_sum = r + gamma * discounted_sum
            returns.insert(0, discounted_sum)

        # Normalize
        returns = np.array(returns)
        returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
        returns = returns.tolist()

        # Calculating loss values to update our network
        history = zip(action_probs_history, critic_value_history, returns)
        actor_losses = []
        critic_losses = []
        for log_prob, value, ret in history:
            # At this point in history, the critic estimated that we would get a
            # total reward = `value` in the future. We took an action with log probability
            # of `log_prob` and ended up receiving a total reward = `ret`.
            # The actor must be updated so that it predicts an action that leads to
            # high rewards (compared to critic's estimate) with high probability.
            diff = ret - value
            actor_losses.append(-log_prob * diff)  # actor loss

            # The critic must be updated so that it predicts a better estimate of
            # the future rewards.
            critic_losses.append(
                huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
            )

        # Backpropagation
        loss_value = sum(actor_losses) + sum(critic_losses)
        grads = tape.gradient(loss_value, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))

        # Clear the loss and reward history
        action_probs_history.clear()
        critic_value_history.clear()
        rewards_history.clear()

    # Log details
    episode_count += 1
    template = "running reward: {:.2f} at episode {}"
    print(template.format(running_reward, episode_count))

    with open(logfile, 'a') as fd:
        fd.write(str(running_reward) + "," + str(episode_reward) + "," + str(episode_count) + "\n")

    if (running_reward / max_steps_per_episode) > 18:  # Condition to consider the task solved
        print("Solved at episode {}!".format(episode_count))
        break

env.close()
