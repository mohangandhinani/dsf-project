from adjudicator import Adjudicator
from greedyAgent import GreedyAgent
from randomAgent import RandomAgent
from agent import Agent
from greedy_baseline import PropertyGreedyAgent

def runAgents():
    agentTwo = PropertyGreedyAgent(2)
    # agentTwo = RandomAgent(2)
    agentOne = Agent(1)
    adjudicator = Adjudicator()
    result = adjudicator.runGame(agentOne, agentTwo)
    return result[0]


# for i in range(6):
onewinner = 0
for i in range(100):
    winner = runAgents()
    if winner == 1:
        onewinner += 1

print(onewinner)
