from adjudicator import Adjudicator
from greedyAgent import GreedyAgent
from randomAgent import RandomAgent
from agent import Agent


def runAgents():
    agentOne = GreedyAgent(1)
    agentTwo = Agent(2)
    # agentTwo = RandomAgent(2)
    adjudicator = Adjudicator()
    result = adjudicator.runGame(agentOne, agentTwo)
    return result[0]


onewinner = 0
for i in range(100):
    winner = runAgents()
    if winner == 1:
        onewinner += 1

print(onewinner)
