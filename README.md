# Monopoly

Data Science Project CSE 519
Monopoly game playing Agent

## Run the code
```
Running the Simulator:
python3 run.py

Running the agents individually:
python3 agent.py
python3 randomAgent.py
python3 property_greedy_agent.py
python3 rl_env.py
```

## Agents
**[Strategic Agent](agent.py)**
> Contains all the code which implements the strategic agent 

**[Random Agent](randomAgent.py)**
> This is a baseline agent. All the decisions taken by the agent are random and chosen from a legal action space. 

**[Greedy Agent](property_greedy_agent.py)**
> This is also a baseline agent. This agent greedily tries to maximize the properties acquired.

**[Reinforcement Learning Agent](/gym-rl/gym_rl/envs/rl_env.py)**
> Contains all the code which implements the Reinforcement Learning based agent

## Supporting files
**[Agents comparator](run.py)**
> Agent comparator invokes different agents and runs games against two agents and presents the win statistics.

**[Agent Constants](agent_constants.py)**
> This is a helper file which has all the constants used by different agents

**[gym environment](gym-rl)**
> Contains all the files needed for creating gym environment

## Performance comparision of the strategic agent
![abc](https://user-images.githubusercontent.com/31523851/50037328-01a1be80-ffde-11e8-9e58-1c5a874aea42.JPG)
