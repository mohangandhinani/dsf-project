#TO DO : timeout decorator
from collections import OrderedDict, Counter
from agent_constants import  *
from constants import *

class State(object):
    def __init__(self,state,my_id):
        opponent_id = 2 if id==1 else 1
        self.turn = state[0]
        self.player_properties = state[1]
        self.my_position = state[2][my_id]
        self.opponent_position = state[2][opponent_id]
        self.my_cash = state[3][my_id]
        self.opponent_cash = state[3][opponent_id]
        self.phase = state[4]
        self.payload = state[5]
        self.debt = state[6][1 if my_id==1 else 3]
        self.previous_states  = state[7]

class Agent(object):
    def __init__(self, id=0):
        self.id = id  # Player 1 -> id=1, Player 2 ->id=2
        self.my_streets = OrderedDict({
                                        "Brown" : {},
                                        "Light Blue" : {},
                                        "Green" : {},
                                        "Red" : {},
                                        "Yellow" : {},
                                        "Orange" : {},
                                        "Dark Blue" : {},
                                        "Pink" : {}
                                        })
        self.monopoly_set = set()
        self.build_buffer_cap = 500

    def get_state_object(self,state):
        return State(state,self.id)

    def update_my_streets(self, state):
        for id,property in enumerate(state.player_properties):
            if (self.id ==1 and 0 < int(property) <=4) or (self.id == 2 and -4 <= int(property) < 0):
                square_obj = board[id]
                if square_obj["class"]=="Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    num_houses = abs(property)-1
                    self.my_streets[colour][id] = (build_cost,num_houses)
                    if len(self.my_streets[colour][id]) == square_obj["monopoly_size"]:
                        self.monopoly_set.add(colour)

    def build_house(self,state):
        cash_left = state.my_cash - self.build_buffer_cap
        result_dict = Counter()
        # self.update_my_streets(state)
        for key,value in self.my_streets.items():
            if key not in self.monopoly_set:
                continue
            flag = 0
            for _ in xrange(3):
                for id in sorted(value,key = lambda k:value[k][0]):
                    build_cost, num_houses = value[id]
                    if num_houses<3:
                        if build_cost<=cash_left:
                            result_dict[id]+=1
                            cash_left -= build_cost
                            self.my_streets[key][id][1]+=1
                        else:
                            flag = 1
                            break
                if flag:
                    break
        return [(k,v) for k,v in result_dict.items()]


    def sell_house(self,state):
        debt_left = state.debt
        result_dict = Counter()
        # self.update_my_streets(state)
        for key,value in self.my_streets.items()[::-1]:
            flag = 0
            for _ in xrange(3):
                for id in sorted(value,key = lambda k:value[k][0],reverse=True):
                    build_cost, num_houses = value[id]
                    if num_houses>0:
                        if debt_left>0:
                            result_dict[id]+=1
                            debt_left -= build_cost
                            self.my_streets[key][id][1]-=1
                        else:
                            flag = 1
                            break
                if flag:
                    break
        return [(k,v) for k,v in result_dict.items()]

    def getBMSTDecision(self, state):
        #preprocesing
        state = self.get_state_object(state)
        self.update_my_streets(state)
        #debt to do
        if self.monopoly_set and not debt:
            #build
            self.build_house(state)

        #sell
        self.sell_house(state)

        #mortagage
        #trade


    def respondTrade(self, state):
        pass(done)

    def buyProperty(self, state):
        pass(done)

    def auctionProperty(self, state):
        pass

    def jailDecision(self, state):
        pass(done)


        def receiveState(self, state):
            pass(done)

