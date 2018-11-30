from gym.envs.registration import register

register(
    id='rl-v0',
    entry_point='gym_rl.envs:RLEnv',
)
