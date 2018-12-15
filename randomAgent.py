
import random
from AgentHelper import *
import constants

# list of all past states
# print(state[1][7])
class RandomAgent(object):
    # Player 1 -> id=0(Properties > 0), Player 2 ->id=1(Properties < 0)
    def __init__(self, id=1):
        self.id = id
        if self.id == 1:
            self.index = 0 # properties > 0
        else:
            self.index = 1 # properties < 0

        # if debt choose between mortgage and sell
        # else try trade
        # Priority to mortgage
        #
        # if you have money build houses
        # if opponent has only one property
        # and player wants to complete a color trade it
    def getBSMTDecision(self, state):

        current_debt = getDebt(self.id,state)

        prop = getprop(self.id,state)
        # Mortgage, #TODO trade, SELL
        if current_debt > 0:
            BSMTdecison = random.randint(0,3)
            if len(prop) > 0:
                if BSMTdecison == 0:
                    return ("M",[random.randint(0,len(prop))])
                elif BSMTdecison == 1:
                    return ("S",[(random.randint(0,len(prop)),1)])
                # TODO fix trade
        return ("B",[(random.randint(0,len(prop)),1)])


    def respondTrade(self, state):
            # if it can compelte the monopoly
            # Or others properties are not bought
        if random.randint(0,2) == 0:
            return True
        return False


    def buyProperty(self, state):
        # True if it has money
        current_cash = state[PLAYER_CASH_INDEX][self.id-1]
        # adding 50 jsut to make sure that palyer has minimum cash 
        if current_cash > getprice(state[PLAYER_POSITION_INDEX][self.id-1]):
            if random.randint(0, 2) == 0:
                return True
        return False


    def auctionProperty(self, state):

        propid = state[PHASE_PAYLOAD_INDEX][0]
        propcash = getprice(propid)
        current_cash = state[PLAYER_POSITION_INDEX][self.index]
         
        # if opponent_cash is way high 
        return random.randint(0,min(current_cash,propcash)+1)


    def jailDecision(self, state):
        # if it has card use it
        # if it has money pay it
        decisions = ["R","C","P"]
        decision = random.randint(0, 3)
        if decision == 1:
            if self.id == state[PROPERTY_STATUS_INDEX][CHANCE_GET_OUT_OF_JAIL_FREE]:
                return ("C",CHANCE_GET_OUT_OF_JAIL_FREE)
            elif self.id == state[PROPERTY_STATUS_INDEX][COMMUNITY_GET_OUT_OF_JAIL_FREE]:
                return ("C",COMMUNITY_GET_OUT_OF_JAIL_FREE)
            else:
                return ("R")
        elif decision == 0:
            return ("R")
        return ("C",50)          


    def respondTrade(self, state):
        # If it can complete the monopoly then return true
        decision = random.randint(0,2)
        if decision == 0:
            return True
        return False

    def receiveState(self, state):
        pass

    def respondMortgage(self, state):
            # if it has enough money then release it
        decision = random.randint(0,2)
        if decision == 0:
            return True
        return False
