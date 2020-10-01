"""
Title: Actor Critic Method for MCS Selection in IEEE 802.11p
Author: Anatolij Zubow
Date created: 2020/09/24
Description: Implement Actor Critic Method with fake (mockup) environment.
"""

import gym
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

obs_low = 14
obs_high = 35


class EnvMockup:

   def __init__(self):
       self.NSC = 64
       self.rssi = [np.random.uniform(obs_low, obs_high)] * self.NSC
       
   def seed(self, v):
       self.v = v
       
   def reset(self):
       obs = [obs_low] * self.NSC
       return obs

   def step(self, action):
       if action == 0:
           reward = 9.0
       if action == 1:
           if np.mean(self.rssi) >= obs_low + (obs_high - obs_low) / 2.0:
               reward = 26.0
           else:
               reward = 0.0
       
       self.rssi = [np.random.uniform(obs_low, obs_high)] * self.NSC
       done = False
       #print("Mockup: next state: %.2f, action: %d, reward: %.2f" % (np.mean(self.rssi), action, reward))
       
       return (self.rssi, reward, done, '')

   def close(self):
       print('Buy')

# Configuration parameters for the whole setup
seed = 42
gamma = 0.0 #0.99  # Discount factor for past rewards
min_num_episodes = 500
max_steps_per_episode = 100 # AZU: 10000
env = EnvMockup() #gym.make('grgym:grenv-v0')  # Create the environment
env.seed(seed)
eps = np.finfo(np.float32).eps.item()  # Smallest number such that 1.0 + eps != 1.0

logfile = './agent_test/running_reward.csv'
with open(logfile, 'w') as fd:
    fd.write("\n")

logfile_raw = './agent_test/raw.csv'
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
    Normalize observation to [0, 1] interval
'''
def preprocess_state(state):
    sc_min = 6
    sc_dc = 32
    sc_max = 59

    # remove null carriers
    obsl = state[sc_min:sc_dc]
    obsr = state[sc_dc + 1:sc_max]

    obs = []
    obs.extend(obsl)
    obs.extend(obsr)
    avg_obs = np.mean(obs)

    if avg_obs < obs_low:
        print('warning: low %.2f' % (avg_obs))
        avg_obs = obs_low

    if avg_obs > obs_high:
        print('warning: high %.2f' % (avg_obs))
        avg_obs = obs_high

    x = (avg_obs - obs_low) / (obs_high - obs_low)
    
    # round x to 2 digits behind comma
    x = round(x, 2)
    
    return x

num_inputs = 1 #no_bits
num_actions = 2 #3
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

optimizer = keras.optimizers.Adam(learning_rate=0.1)
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

            # test
            #if last_state >= 0.5:
            #    action = 1
            #else:
            #    action = 0

            action_probs_history.append(tf.math.log(action_probs[0, action]))
            # debug
            actions_in_epoch[action] += 1

            # Apply the sampled action in our environment
            #print("%d: observation: %.2f" % (timestep, state))
            state, reward, done, _ = env.step(action)
            state = preprocess_state(state)
            #print("%d: next state: %.2f, action: %d, reward: %.2f" % (timestep, state, action, reward))
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
            # of `log_prob` and ended up recieving a total reward = `ret`.
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
    #if episode_count % 10 == 0:
    template = "running reward: {:.2f} at episode {}"
    print(template.format(running_reward, episode_count))

    with open(logfile, 'a') as fd:
        fd.write(str(running_reward) + "," + str(episode_count) + "\n")

    if episode_count >= min_num_episodes and (running_reward / max_steps_per_episode) > 17:  # Condition to consider the task solved
        print("Solved at episode {}!".format(episode_count))
        break

env.close()
