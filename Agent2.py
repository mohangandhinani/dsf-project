import gym
import sys
sys.path.append("/Users/tswetha/dsf-project/gym-rl")
import gym_rl
env=gym.make("rl-v0")

class Agent2:
    def __init__(self, id):
        self.id = id

    def getBMSTDecision(self, state):
        return env.getBMST(state)

    def respondTrade(self, state):
        pass

    def buyProperty(self, state):
        pass

    def auctionProperty(self, state):
        pass

    def jailDecision(self, state):
        pass

    def receiveState(self, state):
        pass

