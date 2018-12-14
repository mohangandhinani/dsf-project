# Monopoly

Data Science Project CSE 519
Monopoly game playing AI Agent

## Run the code


## Files
## Random Agent
[Random Agent](/gym-rl/gym_rl/envs/rl_env.py)

**agent.py:**
>Consists of configurations for logging to the monopoly.log file. You can modify the verbosity of logging for different flows of the adjudicator here.

**constants.py:**
>Contains the constant representations such as the board, chance cards and community chest cards that remain static throughout the runtime of the game.

**testcases.py:**
>Consists of all the testcases written for and tested against the adjudicator. Each testcase contains a short description regarding what it is testing. The testcases each define their own Agents to suit their testing requirements. The testcases each receive an instance of the adjudicator as an argument and perform testcase validation by invoking the runGame method and observing the final results.
The program accepts an Adjudicator and 2 Agents as arguments and checks whether the testcase passes for the simulation run.
