from adjudicator import Adjudicator
from greedyAgent import GreedyAgent
from randomAgent import RandomAgent
from property_greedy_agent import PropertyGreedyAgent
from agent import Agent


def runAgents():
    # agentTwo = GreedyAgent(2)
    agentOne = Agent(1)
    agentTwo = RandomAgent(2)
    # agentTwo = PropertyGreedyAgent(2)
    adjudicator = Adjudicator()
    result = adjudicator.runGame(agentOne, agentTwo)
    return result[0]


onewinner = 0
for i in range(100):
    winner = runAgents()
    if winner == 1:
        onewinner += 1

print(onewinner)
