from collections import OrderedDict, Counter
from agent_constants import  *
from constants import *


class State(object):
    def __init__(self, state, my_id):
        opponent_id = 2 if id == 1 else 1
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
    # TO DO : timeout decorator
    def __init__(self, id):
        self.id = id  # Player 1 -> id=1, Player 2 -> id=2
        self.my_streets = OrderedDict({
            "Brown": {},
            "Light Blue": {},
            "Green": {},
            "Red": {},
            "Yellow": {},
            "Orange": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.monopoly_set = set()
        self.build_buffer_cap = 500
        self.buying_limit = 300

    @staticmethod
    def get_turns_left(stateobj):
        return 99 - stateobj.turn

    def get_other_agent(self):
        if self.id == 1:
            return 2
        else:
            return 1

    def get_state_object(self, state):
        return State(state, self.id)

    def update_my_streets(self, state):
        for id, property in enumerate(state.player_properties):
            if (self.id ==1 and 0 < int(property) <= 4) or (self.id == 2 and -4 <= int(property) < 0):
                square_obj = board[id]
                if square_obj["class"]=="Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    num_houses = abs(property)-1
                    self.my_streets[colour][id] = (build_cost,num_houses)
                    if len(self.my_streets[colour][id]) == square_obj["monopoly_size"]:
                        self.monopoly_set.add(colour)

    def build_house(self, state):
        cash_left = state.my_cash - self.build_buffer_cap
        result_dict = Counter()
        # self.update_my_streets(state)
        for key, value in self.my_streets.items():
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

    def sell_house(self, state):
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
        # preprocesing
        state = self.get_state_object(state)
        self.update_my_streets(state)
        # debt to do
        if self.monopoly_set and not debt:
            # build
            self.build_house(state)

        # sell
        self.sell_house(state)

        # mortagage
        # trade

    def respondTrade(self, state):
        pass

    def buyProperty(self, state):
        stateobj = self.get_state_object(state)

        # Check if we reached buying cap
        if stateobj.my_cash <= self.buying_limit:
            return False

        # check if less number of turns left
        if self.get_turns_left(stateobj) < 20:
            return False

        # get class of property landed on
        propertyId = stateobj.my_position
        space = board[propertyId]
        if space['class'] == 'Railroad':
            # blind yes!
            return True
        elif space['class'] == 'Street':
            # Check if it is forming monopoly
            monopoly_size = space['monopoly_size']
            num_props_cg = len(self.my_streets[space['monopoly']])
            if num_props_cg + 1 == monopoly_size:
                # definitely buy
                return True

            # Check if it is important to opponent
            propertyStatus = [prop for prop in state[1]]
            opp_id = self.get_other_agent()
            is_imp = True
            for propid in space['monopoly_group_elements']:
                if (opp_id == 1 and not 1 <= propertyStatus[propid] <= 7) or \
                        (opp_id == 2 and not -7 <= propertyStatus[propid] <= -1):
                    is_imp = False
            if is_imp:
                return True

            # Check if it is important to us
            if space['monopoly'] in ['Orange', 'Red', 'Yellow', 'Light Blue']:
                return True
            else:
                # Look for auction if we are not interested in property
                return False

        elif space['class'] == 'Utility':
            # TBD
            return False

    def auctionProperty(self, state):
        pass

    def jailDecision(self, state):
        pass

    def receiveState(self, state):
        pass

