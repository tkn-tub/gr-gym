from gym.envs.registration import registry, register, make, spec

register(
    id='gr_env-v0',
    entry_point='gym.envs.algorithmic:CopyEnv',
    max_episode_steps=200,
    reward_threshold=25.0,
)
