import logging
from gym.envs.registration import registry, register, make, spec

logger = logging.getLogger(__name__)

print("test")

register(
    id='grenv-v0',
    entry_point='grgym.envs:GrEnv'
)
