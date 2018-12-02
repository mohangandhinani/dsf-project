import gym
import sys
sys.path.append("/Users/tswetha/dsf-project/gym-rl")
env=gym.make("rl-v0")

class Agent2:
    def __init__(self, id):
        self.id = id

    def getBMSTDecision(self, state):
        return env.getBMST(state)

    def respondTrade(self, state):
        return env.respondTrade(state)

    def buyProperty(self, state):
        return env.respondTrade(state)

    def auctionProperty(self, state):
        return env.auctionProperty(state)

    def jailDecision(self, state):
        return env.jailDecision(state)

    def receiveState(self, state):
        pass

