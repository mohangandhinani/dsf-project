# Monopoly

Data Science Project CSE 519
Monopoly game playing AI Agent
Done by Team 007

Team Members:
Pragesh Jagnani
Sanjay Mathew Thomas
Varun Hegde

## Install the Dependencies

```
pip install -r requirements.txt
```

## Run the code

```
export FLASK_APP=app.py
flask run

To run the adjudicator program without the UI implementation, run:
from adjudicator import Adjudicator
from agent import Agent
agentOne = Agent(1)
agentTwo = Agent(2)
adjudicator = Adjudicator()
adjudicator.runGame(agentOne, agentTwo)

To run testcases, run:
python testcases.py

To run the user interface
cd react-user-interface
npm install
npm start

```

## App Structure
The master branch consists of the implementation of the Adjudicator for the monopoly game.
The implementation also consists of a UI for going through the various game states after a game has been completed. 
NOTE: The UI currently shows the board representation and basic information about each Agent on any given turn such as properties owned, cash constructions on each property etc. Finer information regarding the state still remains to be implemented for the UI and is in progress.

app.py is the controller.  
templates for rendering templates.  
static has all static assets js, css and images.

adjudicator.py:
Consist of the actual implementation of the Adjudicator. The game is started by invoking the method: 

runGame(agentOne,agentTwo,diceThrows=None,chanceCards=None,communityCards=None)
This method accepts 2 Agents and runs the game. Over the course of the game, it determines which Agent is the winner.
The other 3 parameters are for testing purposes only.
diceThrows: used to pass in an array of dice rolls (each a 2x1 array of 2 die). The test case would be evaluated by taking a dice roll from the array and applying it instead of using the random die.
chanceCards: an array of ids of chance cards to be used for a particular testcases. For referencing the values of the ids, please check constants.py.
chanceCards: an array of ids of community chest cards to be used for a particular testcases. For referencing the values of the ids, please check constants.py.

config.py
Consists of configurations for logging to the monopoly.log file. You can modify the verbosity of logging for different flows of the adjudicator here.

constants.py
Contains the constant representations such as the board, chance cards and community chest cards that remain static throughout the runtime of the game.

testcases.py:
Consists of all the testcases written for and tested against the adjudicator. Each testcase contains a short description regarding what it is testing. The testcases each define their own Agents to suit their testing requirements. The testcases each receive an instance of the adjudicator as an argument and perform testcase validation by invoking the runGame method and observing the final results.
The program accepts an Adjudicator and 2 Agents as arguments and checks whether the testcase passes for the simulation run.
