from collections import OrderedDict, Counter
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
        self.debt = state[6][1 if my_id == 1 else 3]
        self.previous_states = state[7]


class Agent(object):
    # TO DO : timeout decorator
    def __init__(self, id):
        self.id = id  # Player 1 -> id=1, Player 2 -> id=2
        self.my_streets = OrderedDict({
            "Brown": {},
            "Light Blue": {},  # key is property id value is (buildcost, num houses, price)
            "Green": {},
            "Red": {},
            "Yellow": {},
            "Orange": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.utilities = {}
        self.rail_roads = {}  # id:price
        self.monopoly_set = set()
        self.build_buffer_cap = 500
        self.unmortgage_cap = 300
        self.buying_limit = 300
        self.mortagaged_cgs = []  # tuple of color, id, unmortgage price

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

    def getBMSTDecision(self, state):
        # preprocesing
        state = self.get_state_object(state)
        self.update_my_properties(state)
        # TODO : bsmt decision making and debt should always clear
        # debt to do
        if self.monopoly_set and not debt:
            # build
            self.build_house(state)

        # sell
        self.sell_house(state)

        # mortagage
        # trade

    def update_my_properties(self, state):
        for id, property in enumerate(state.player_properties):
            if (self.id == 1 and 0 < int(property) <= 4) or (self.id == 2 and -4 <= int(property) < 0):
                square_obj = board[id]
                price = square_obj["price"]
                if square_obj["class"] == "Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    num_houses = abs(property) - 1
                    self.my_streets[colour][id] = (build_cost, num_houses, price)
                    if len(self.my_streets[colour][id]) == square_obj["monopoly_size"]:
                        self.monopoly_set.add(colour)
                elif square_obj["class"] == "Utility":
                    self.utilities[id] = (price)
                elif square_obj["class"] == "Railroad":
                    self.rail_roads[id] = (price)

    def build_house(self, state):
        cash_left = state.my_cash - self.build_buffer_cap
        result_dict = Counter()
        # self.update_my_streets(state)
        for key, value in self.my_streets.items():
            if key not in self.monopoly_set:
                continue
            flag = 0
            for _ in range(3):
                for id in sorted(value, key=lambda k: value[k][0]):
                    build_cost, num_houses = value[id]
                    if num_houses < 3:
                        if build_cost <= cash_left:
                            result_dict[id] += 1
                            cash_left -= build_cost
                            self.my_streets[key][id][1] += 1
                        else:
                            flag = 1
                            break
                if flag:
                    break
        return [(k, v) for k, v in result_dict.items()]

    def mortagage_properties(self, state):
        # note : only 50%
        debt_left = state.debt
        mortagage_properties_result = []
        # 1) Check 1-10 cells properties
        # 1st mortagage railroad
        rail_road_key = self.rail_roads.keys()[0]
        if len(self.rail_roads) == 1 and 0 < rail_road_key < 10:
            debt_left -= 0.5 * self.rail_roads[rail_road_key]
            del self.rail_roads[rail_road_key]
            mortagage_properties_result.append(rail_road_key)
        if debt_left <= 0:
            return mortagage_properties_result
        # check for street which is not CG
        marker = []
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set :
                for id, tup in value.items():
                    if tup[1] != 0:
                        continue
                    if 0 < int(id) < 10:
                        debt_left -= 0.5 * tup[2]
                        mortagage_properties_result.append(id)
                        marker.append((color, id))
                        if debt_left <= 0:
                            break
        # delete keys
        for color, id in marker:
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result
        # single utility
        if len(self.utilities) == 1:
            key = self.utilities.keys()[0]
            mortagage_properties_result.append(key)
            debt_left -= 0.5 * self.utilities[key]
            self.utilities = {}
        if debt_left <= 0:
            return mortagage_properties_result
        # single railroad
        if len(self.rail_roads) == 1:
            key = self.rail_roads.keys()[0]
            mortagage_properties_result.append(key)
            debt_left -= 0.5 * self.rail_roads[key]
            self.rail_roads = {}
        if debt_left <= 0:
            return mortagage_properties_result
        # both utilities
        if len(self.utilities) == 2:
            marker = []
            for id, value in self.utilities.items():
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * value
                marker.append(id)
                if debt_left < 0:
                    break
        for id in marker:
            del self.utilities[id]
        if debt_left <= 0:
            return mortagage_properties_result
        #single street property
        marker = []
        for color,dct in self.my_streets.items()[::-1]:
            if len(dct)==1:
                id = dct.keys()[0]
                if dct[id][1] != 0:
                    continue
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * int(dct[id][2])
                marker.append((color,id))
                if debt_left < 0:
                    break
        for color,id in marker:
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result
        # sell rail road
        marker = []
        for id,price in self.rail_roads.items():
            mortagage_properties_result.append(id)
            debt_left -= 0.5 * price
            marker.append(id)
            if debt_left < 0:
                break
        for id in marker:
            del self.rail_roads[id]
        if debt_left <= 0:
            return mortagage_properties_result
        #sell all street properties
        marker = []
        for color, dct in self.my_streets.items()[::-1]:
            for id,tup in dct.items():
                if dct[id][1] != 0:
                    continue
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * int(tup[2])
                marker.append((color, id))
                if debt_left < 0:
                    break
        for color, id in marker:
            if color in self.monopoly_set:
                self.mortagaged_cgs.append((color,id,self.my_streets[color][id][2]*0.55))
                self.monopoly_set.remove(color)
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result
        return mortagage_properties_result

    def unmortgage_property(self, state):
        unmortgage_result = []
        cash_left = state.my_cash - self.unmortgage_cap
        for color,id,price in self.mortagaged_cgs:
            if cash_left > price:
                pass

    def sell_house(self, state):
        # TODO :: if we are switching from sell to morgage then save state
        debt_left = state.debt
        result_dict = Counter()
        # self.update_my_streets(state)
        for key, value in self.my_streets.items()[::-1]:
            flag = 0
            for _ in range(3):
                for id in sorted(value, key=lambda k: value[k][0], reverse=True):

                    build_cost, num_houses = value[id]
                    if num_houses > 0:
                        if debt_left > 0:
                            result_dict[id] += 1
                            debt_left -= build_cost
                            self.my_streets[key][id][1] -= 1
                        else:
                            flag = 1
                            break
                if flag:
                    break
        return [(k, v) for k, v in result_dict.items()]

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
