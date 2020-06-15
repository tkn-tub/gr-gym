import gym

env = gym.make('gr_env-v0')
obs = env.reset()

while True:
  action = 0
  obs, reward, done, info = env.step(action)

  if done:
    break
env.close()
