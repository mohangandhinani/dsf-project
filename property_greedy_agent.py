import random
from collections import OrderedDict, Counter
from AgentHelper import *
from constants import board

class State(object):
    def __init__(self, state, id):
        my_id = 0 if id == 1 else 1
        opponent_id = 1 if id == 1 else 0
        self.turn = state[0]
        self.player_properties = state[1][:-2]
        self.jail_cards = state[1][40:]
        self.my_position = state[2][my_id]
        self.opponent_position = state[2][opponent_id]
        self.my_cash = state[3][my_id]
        self.opponent_cash = state[3][opponent_id]
        self.phase = state[4]
        self.payload = state[5]
        tmp_debt = state[6][1 if my_id == 0 else 3]
        if self.my_cash > tmp_debt:
            self.debt= 0
        else:
            self.debt = tmp_debt
        self.opponent_debt = state[6][1 if opponent_id == 0 else 3]
        self.previous_states = state[7]

#This agent always buys all properties it lands on and doesnt want to lose it's
#properties in any case
class PropertyGreedyAgent(object):
    # Player 1 -> id=0(Properties > 0), Player 2 ->id=1(Properties < 0)
    def __init__(self, id=1):
        self.id = id
        if self.id == 1:
            self.index = 0  # properties > 0
        else:
            self.index = 1  # properties < 0
        self.monopoly_set = set()
        #Not using ordered dict here as there is no preference order
        self.my_streets = {
            "Pink": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Yellow": {},
            "Light Blue": {},
            "Dark Blue": {},
            "Red": {},
            "Green": {},
            "Orange": {},
        }
        self.utilities = {}
        self.rail_roads = {}  # id:price
        self.build_buffer_cap = 500
        self.unmortgage_cap = 300
        self.buying_limit = 300
        self.auction_limit = 200
        self.profitable_deal_threshold = 100
        self.mortagaged_cgs = []  # tuple of color, id, unmortgage price
        self.opp_streets = {
            "Pink": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Yellow": {},
            "Dark Blue": {},
            "Light Blue": {},
            "Red": {},
            "Green": {},
            "Orange": {},
        }
        self.opp_utilities = {}
        self.opp_rail_roads = {}  # id:price
        self.opp_mortgaged_props = {}

    def get_other_agent(self):
        return 2 if self.id == 1 else 1

    def get_state_object(self, state):
        return State(state, self.id)

    def update_my_properties(self, stateobj):
        for id, status in enumerate(stateobj.player_properties):
            if (self.id == 1 and 0 < int(status) <= 4) or (self.id == 2 and -4 <= int(status) < 0):
                square_obj = board[id]
                price = square_obj["price"]
                if square_obj["class"] == "Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    num_houses = abs(status) - 1
                    self.my_streets[colour][id] = [build_cost, num_houses, price]
                    if len(self.my_streets[colour]) == square_obj["monopoly_size"]:
                        self.monopoly_set.add(colour)
                elif square_obj["class"] == "Utility":
                    self.utilities[id] = price
                elif square_obj["class"] == "Railroad":
                    self.rail_roads[id] = price

    def update_opp_props(self, stateobj):
        opp_id = self.get_other_agent()
        for id, status in enumerate(stateobj.player_properties):
            if (opp_id == 1 and 0 < int(status) <= 7) or (opp_id == 2 and -7 <= int(status) < 0):
                square_obj = board[id]
                price = square_obj["price"]
                if (opp_id == 1 and status == 7) or (opp_id == 2 and status == -7):
                    self.opp_mortgaged_props[id] = price
                    continue
                if square_obj["class"] == "Street":
                    colour = square_obj["monopoly"]
                    build_cost = square_obj["build_cost"]
                    num_houses = abs(status) - 1
                    self.opp_streets[colour][id] = (build_cost, num_houses, price)
                    # if len(self.opp_streets[colour][id]) == square_obj["monopoly_size"]:
                    #     self.monopoly_set.add(colour)
                elif square_obj["class"] == "Utility":
                    self.opp_utilities[id] = price
                elif square_obj["class"] == "Railroad":
                    self.opp_rail_roads[id] = price

    def build_house(self, stateobj):
        cash_left = stateobj.my_cash - self.build_buffer_cap
        result_dict = Counter()
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                continue
            for id, tup in value.items():
                build_cost, num_houses, p = value[id]
                if num_houses < 4:
                    if build_cost <= cash_left:
                        result_dict[id] += 1
                        cash_left -= build_cost
                        self.my_streets[color][id][1] += 1
        return [(k, v) for k, v in result_dict.items()]

    #This method returns the properties that the player owns by
    #sorting them in the order of the price and returning sufficient
    #properties that allow him to clear his debt.
    def mortagage_properties(self, stateobj):
        debt_left = stateobj.debt
        all_props = []
        mortagage_properties_result= []
        for color, value in self.my_streets.items():
            for id, tup in value.items():
                all_props.append((id, tup[2]))

        all_props.extend((k,v) for k,v in self.utilities.items())
        all_props.extend((k,v) for k,v in self.rail_roads.items())

        #sorting all props by price
        all_props.sort(key=lambda x:x[1])

        for id,price in all_props:
            mortagage_properties_result.append(id)
            debt_left -= 0.5 * price
            if debt_left <=0:
                break
        return mortagage_properties_result

    def get_useless_props(self, stateobj):
        props_to_trade = []

        # check for street which is not CG
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                for id, tup in value.items():
                    if tup[1] != 0:
                        continue
                    if id not in props_to_trade:
                        props_to_trade.append((id,tup[2]))

        props_to_trade.sort(key= lambda x:x[1])
        return [id for id, price in props_to_trade]

    #tries to unmortgage as many properties as possible
    #depending on the cash left, sorts the properties by price and
    #returns all properties
    def unmortgage_property(self, stateobj):
        unmortgage_result = []
        cash_left = stateobj.my_cash - self.unmortgage_cap
        mortgaged_props=[]
        for id, property in enumerate(stateobj.player_properties):
            if (self.id == 1 and property == 7) or (self.id == 2 and property == -7):
                square_obj = board[id]
                price = square_obj["price"] * 0.55
                mortgaged_props.append((id, price))

        mortgaged_props.sort(key= lambda x:x[1])
        for id, price in mortgaged_props:
            if cash_left > price:
                cash_left-= price
                unmortgage_result.append(id)
            else:
                break
        return unmortgage_result

    #This agent tries to sell all houses starting with the least order of build costs
    #and tries to clear debt accordingly
    def sell_house(self, stateobj):
        # TODO :: if we are switching from sell to mortgage then save state
        result_dict = Counter()

        marker = []
        debt_left = stateobj.debt
        all_props_with_houses = []
        for color, value in self.my_streets.items():
            for id, tup in value.items():
                if 1 < abs(tup[1]) < 7:
                    all_props_with_houses.append((id, color, tup[0]))

        # sorting all props by price
        all_props_with_houses.sort(key=lambda x: x[2])

        for id, color, build_cost in all_props_with_houses:
            result_dict[id] = build_cost
            debt_left -= build_cost
            self.my_streets[color][id][1] -=1
            marker.append((color,id))
            if debt_left <= 0:
                break
        if debt_left > 0:
            # let it try mortgaging if selling houses does not clear debt
            for colour, id in marker:
                # fixing changes made to my_streets
                self.my_streets[colour][id][1] += 1
            return []
        return [(k, v) for k, v in result_dict.items()]

    def get_trade_option(self, stateobj):
        # Get opponent properties - utilities, railroads, mortgaged properties, cgs, other props
        self.update_opp_props(stateobj)

        # Try to get properties to request by looking at CG
        self.update_my_properties(stateobj)
        props_req = []
        for color, values in self.my_streets.items():
            if color in self.monopoly_set:
                continue
            if not values:
                continue
            any_id = list(values.keys())[0]
            grp_elements = board[any_id]['monopoly_group_elements']
            if len(grp_elements) == len(values):
                grp_elements.append(any_id)
                props_req.append(list(set(grp_elements) - set(values))[0])


        useless_props = self.get_useless_props(stateobj)

        #try to get his rail roads
        if len(self.opp_rail_roads) > 0:
            id = list(self.opp_rail_roads.keys())[0]
            cash_to_match = board[id]['price'] + stateobj.debt
            for useless_prop in useless_props:
                cash_to_match -= board[useless_prop]['price']
                props_req.append(useless_prop)

        #try to get his utilities
        if len(self.utilities) > 0:
            id = list(self.utilities.keys())[0]
            cash_to_match = board[id]['price'] + stateobj.debt
            for useless_prop in useless_props:
                cash_to_match -= board[useless_prop]['price']
                props_req.append(useless_prop)

        random.shuffle(props_req)
        if props_req and useless_props:
            for prop in props_req:
                tmp_lst = []
                cash_to_match = board[prop]['price'] + stateobj.debt
                for id in useless_props:
                    # trying all combinations of useless prop and prop to offer
                    cash_to_match -= board[id]['price']
                    tmp_lst.append(id)
                    if cash_to_match > 0:
                        continue
                    else:
                        cash_req = abs(cash_to_match)
                        return 'T', 0, tmp_lst, cash_req, [prop]
                if cash_to_match > 0:
                    continue
        elif not useless_props:
            for prop in props_req:
                cash_offer = board[prop]['price']
                if stateobj.my_cash >= cash_offer + 300:
                    return 'T', cash_offer, [], 0, [prop]

        return None

    def getBSMTDecision(self, state):
        # preprocessing
        stateobj = self.get_state_object(state)
        self.update_my_properties(stateobj)
        if stateobj.debt == 0:
            if self.monopoly_set:
                lst_houses = self.build_house(stateobj)
                if lst_houses:
                    return "B", lst_houses
            else:
                lst_properties = self.unmortgage_property(stateobj)
                if lst_properties:
                    return "M", lst_properties
        else:
            # bsmt decision making
            # debt should always be cleared: choose sell or mortgage accordingly
            # sell
            lst_houses = self.sell_house(stateobj)
            if lst_houses:
                return "S", lst_houses
            # mortgage
            lst_properties = self.mortagage_properties(stateobj)
            if lst_properties:
                return "M", lst_properties
        return self.get_trade_option(stateobj)

    def value_of_properties(self, properties_lst):
        total_value = 0
        for id in properties_lst:
            if id in self.opp_mortgaged_props:
                total_value += board[id]["price"] * 0.45
            else:
                total_value += board[id]["price"]
        return total_value

    def net_trade_deal_amount(self, cash_offered, cash_requested, properties_offered, properties_requested):
        return cash_offered + self.value_of_properties(properties_offered) - cash_requested - self.value_of_properties(
            properties_requested)

    #Always accept the trade if the net value you get is greater
    def respondTrade(self, state):
        stateobj = self.get_state_object(state)
        if len(stateobj.payload) == 4:
            cash_offer, properties_offered, cash_requested, properties_requested = stateobj.payload
        else:
            bool, cash_offer, properties_offered, cash_requested, properties_requested = stateobj.payload
        net_value= self.net_trade_deal_amount(cash_offer, cash_requested, properties_offered, properties_requested)
        if net_value > 0:
            return True
        return False

    def buyProperty(self, state):
        # always buy if you have cash
        current_cash = state[PLAYER_CASH_INDEX][self.id - 1]
        if current_cash > getprice(state[PLAYER_POSITION_INDEX][self.id - 1]):
            return True
        return False

    def auctionProperty(self, state):

        propid = state[PHASE_PAYLOAD_INDEX][0]
        propcash = getprice(propid)
        current_cash = state[PLAYER_POSITION_INDEX][self.index]

        #always try to win the auction. Trying to get the property at the original price
        if current_cash > propcash:
            return propcash
        #returning current cash - 50, just to keep a buffer
        return current_cash-50

    def jailDecision(self, state):
        # if it has card use it
        # if it has money pay it or roll with equal probability
        current_cash = state[PLAYER_POSITION_INDEX][self.index]

        flag = -1 if self.id == 2 else 1
        if flag == state[PROPERTY_STATUS_INDEX][CHANCE_GET_OUT_OF_JAIL_FREE]:
            return 'C', 40
        elif flag == state[PROPERTY_STATUS_INDEX][COMMUNITY_GET_OUT_OF_JAIL_FREE]:
            return 'C', 41
        else:
            if random.random() < 0.5 and current_cash > 50:
                return 'P', None
        return ("R",None)


    def receiveState(self, state):
        pass

