# Monopoly

Data Science Project CSE 519
Monopoly game playing Agent

## Run the code
```
Running Agents
python3 rl_env.py
python3 agent.py
python3 randomAgent.py
python3 property_greedy_agent.py

Running Comparator
python3 run.py
```

## Agents
**[Strategic Agent](agent.py)**
> Contains all the code which implements the strategic agent 

**[Reinforcement Learning Agent](/gym-rl/gym_rl/envs/rl_env.py)**
> Constains all the code which implements the reinforcewment learning based agent

**[Random Agent](randomAgent.py)**
> This is a base line agent. All the decisions taken by the agent are random and chosen from a leagal action space. 

**[Greedy Agent](property_greedy_agent.py)**
> This is also a baseline agent .This agent greedly tries to maximize the properties acquired.


## Supporting files
**[Agents comparator](run.py)**
> Agent comparator invokes different agents and runs games against two agents and presents the win statistics.

**[Agent Constants](agent_constants.py)**
> This is a helper file which has all the constants used by different agents

**[gym environment](gym-rl)**
> contains all the files needed for creating gym environment

## Performance comparision of the strategic agent
![abc](https://user-images.githubusercontent.com/31523851/50037328-01a1be80-ffde-11e8-9e58-1c5a874aea42.JPG)
