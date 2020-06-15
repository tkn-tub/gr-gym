import gym

env = gym.make('grgym:grenv-v0')
obs = env.reset()

while True:
  action = 0
  obs, reward, done, info = env.step(action)

  if done:
    break
env.close()
