import random
from collections import OrderedDict, Counter

from AgentHelper import *
import constants
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
class AlwaysBuyAgent(object):
    # Player 1 -> id=0(Properties > 0), Player 2 ->id=1(Properties < 0)
    def __init__(self, id=1):
        self.id = id
        if self.id == 1:
            self.index = 0  # properties > 0
        else:
            self.index = 1  # properties < 0
        self.monopoly_set = set()
        self.my_streets = OrderedDict({
            "Orange": {},
            "Red": {},
            "Yellow": {},
            "Light Blue": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Green": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.utilities = {}
        self.rail_roads = {}  # id:price
        self.build_buffer_cap = 500
        self.unmortgage_cap = 300
        self.buying_limit = 300
        self.auction_limit = 200
        self.profitable_deal_threshold = 100
        self.mortagaged_cgs = []  # tuple of color, id, unmortgage price
        self.opp_streets = OrderedDict({
            "Orange": {},
            "Red": {},
            "Yellow": {},
            "Light Blue": {},
            "Brown": {},  # key is id value is (buildcost, num houses, price)
            "Green": {},
            "Dark Blue": {},
            "Pink": {}
        })
        self.opp_utilities = {}
        self.opp_rail_roads = {}  # id:price
        self.opp_mortgaged_props = {}

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

    def build_house(self, stateobj):
        cash_left = stateobj.my_cash - self.build_buffer_cap
        result_dict = Counter()
        # self.update_my_streets(stateobj)
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                continue
            flag = 0
            for _ in range(3):
                for id in sorted(value, key=lambda k: value[k][0]):
                    build_cost, num_houses, p = value[id]
                    if num_houses < 3:
                        if build_cost <= cash_left:
                            result_dict[id] += 1
                            cash_left -= build_cost
                            self.my_streets[color][id][1] += 1
                        else:
                            flag = 1
                            break
                if flag:
                    break
        return [(k, v) for k, v in result_dict.items()]

    def mortagage_properties(self, stateobj):
        # note : only 50%
        debt_left = stateobj.debt
        mortagage_properties_result = []

        # 1) Check 1-10 cells properties
        # 1st mortgage railroad
        if self.rail_roads:
            rail_road_key = list(self.rail_roads.keys())[0]
            if len(self.rail_roads) == 1 and 0 < rail_road_key < 10:
                debt_left -= 0.5 * self.rail_roads[rail_road_key]
                del self.rail_roads[rail_road_key]
                mortagage_properties_result.append(rail_road_key)
            if debt_left <= 0:
                return mortagage_properties_result

        # check for street which is not CG
        marker = []
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
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
            key = list(self.utilities.keys())[0]
            mortagage_properties_result.append(key)
            debt_left -= 0.5 * self.utilities[key]
            self.utilities = {}
        if debt_left <= 0:
            return mortagage_properties_result

        # single railroad
        if len(self.rail_roads) == 1:
            key = list(self.rail_roads.keys())[0]
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

        # single street property
        marker = []
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            if len(dct) == 1:
                id = list(dct.keys())[0]
                if dct[id][1] != 0:
                    continue
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * int(dct[id][2])
                marker.append((color, id))
                if debt_left < 0:
                    break
        for color, id in marker:
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result

        # sell rail road
        marker = []
        for id, price in self.rail_roads.items():
            self.mortagaged_cgs.append(("Railroad", id, price * 0.55))
            mortagage_properties_result.append(id)
            debt_left -= 0.5 * price
            marker.append(id)
            if debt_left < 0:
                break
        for id in marker:
            del self.rail_roads[id]
        if debt_left <= 0:
            return mortagage_properties_result

        # sell all street properties
        marker = []
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            for id, tup in dct.items():
                if dct[id][1] != 0:
                    continue
                mortagage_properties_result.append(id)
                debt_left -= 0.5 * int(tup[2])
                marker.append((color, id))
                if debt_left < 0:
                    break
        for color, id in marker:
            if color in self.monopoly_set:
                self.mortagaged_cgs.append((color, id, self.my_streets[color][id][2] * 0.55))
                self.monopoly_set.remove(color)
            del self.my_streets[color][id]
        if debt_left <= 0:
            return mortagage_properties_result

        return mortagage_properties_result

    def get_useless_props(self, stateobj):
        props_to_trade = []
        # 1) Check 1-10 cells properties
        # check for street which is not CG
        for color, value in self.my_streets.items():
            if color not in self.monopoly_set:
                for id, tup in value.items():
                    if tup[1] != 0:
                        continue
                    if 0 < int(id) < 10:
                        props_to_trade.append(id)

        # single utility
        if len(self.utilities) == 1:
            key = list(self.utilities.keys())[0]
            props_to_trade.append(key)

        # Mortgaged property
        mgt_cg_ids = set([t[1] for t in self.mortagaged_cgs])
        for id, status in enumerate(stateobj.player_properties):
            if (self.id == 1 and status == 7) or (self.id == 2 and status == -7):
                if id in mgt_cg_ids:
                    continue
                props_to_trade.append(id)

        # single street property
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            if len(dct) == 1 and color not in ['Orange', 'Red', 'Yellow']:
                id = list(dct.keys())[0]
                if dct[id][1] != 0:
                    continue
                props_to_trade.append(id)

        res = []
        for id in props_to_trade:
            space = board[id]
            # Check if his street monopoly is getting formed
            color = space['monopoly']
            if color != "Railroad" and color != "Utility":
                if space['monopoly_size'] - len(self.opp_streets[color]) == 1:
                    continue
            # Check if his utility monopoly is getting formed
            if space['monopoly_size'] - len(self.opp_utilities) == 1:
                continue
            # Check if his railroad monopoly is getting formed
            if space['monopoly_size'] - len(self.opp_rail_roads) == 1:
                continue
            res.append(id)

        # Buffer of all props to clear debt
        buffer_props = []
        for color in list(self.my_streets.keys())[::-1]:
            dct = self.my_streets[color]
            for id, tup in dct.items():
                if id not in res:
                    buffer_props.append(id)

        return res, buffer_props

    def unmortgage_property(self, stateobj):
        unmortgage_result = []
        cash_left = stateobj.my_cash - self.unmortgage_cap
        for color, id, price in sorted(self.mortagaged_cgs, key=lambda x: self.preference_order[x[0]]):
            if cash_left > price:
                cash_left -= price
                unmortgage_result.append(id)
            else:
                return unmortgage_result

        # unmortgage all other properties if u have turns
        num_turn_left = self.get_turns_left(stateobj)
        if cash_left and num_turn_left > 20:
            for id, property in enumerate(stateobj.player_properties):
                # TODO :: unmortgage in preference order
                if (self.id == 1 and property == 7) or (self.id == 2 and property == -7):
                    square_obj = board[id]
                    price = square_obj["price"] * 0.55
                    if float(cash_left) > price:
                        cash_left -= price
                        unmortgage_result.append(id)
                    else:
                        return unmortgage_result
        else:
            return unmortgage_result

    def sell_house(self, stateobj):
        # TODO :: if we are switching from sell to mortgage then save state
        debt_left = stateobj.debt
        result_dict = Counter()
        # self.update_my_streets(stateobj)

        marker = []
        for key in list(self.my_streets.keys())[::-1]:
            value = self.my_streets[key]
            flag = 0
            for _ in range(3):
                for id in sorted(value, key=lambda k: value[k][0], reverse=True):

                    build_cost, num_houses, p = value[id]
                    if num_houses > 0:
                        if debt_left > 0:
                            result_dict[id] += 1
                            debt_left -= build_cost
                            self.my_streets[key][id][1] -= 1
                            marker.append((key, id))
                        else:
                            flag = 1
                            break
                if flag:
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

        # Try to get properties to request by looking at CG in
        # preference order (O,R,Y only) + utility + railroad
        self.update_my_properties(stateobj)
        props_req = []
        for color, values in self.my_streets.items():
            if color in self.monopoly_set or color in ['Light Blue', 'Brown', 'Green', 'Dark Blue', 'Pink']:
                continue
            if not values:
                continue
            any_id = list(values.keys())[0]
            grp_elements = board[any_id]['monopoly_group_elements']
            if len(grp_elements) == len(values):
                grp_elements.append(any_id)
                props_req.append(list(set(grp_elements) - set(values))[0])

        useless_props, buffer = self.get_useless_props(stateobj)
        giveaway_props = copy.deepcopy(useless_props)
        giveaway_props.extend(buffer)

        # MUST TODO: randomise this invocation
        # Strategy 1 (taking care of debt + requesting imp props)
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

        # Strategy 2: If we have one railroad, get railroad from him
        # & give prop without forming cg to him
        if len(self.rail_roads) > 0 and len(self.opp_rail_roads) > 0:
            tmp_lst = []
            id = list(self.opp_rail_roads.keys())[0]
            cash_to_match = board[id]['price'] + stateobj.debt
            for useless_prop in useless_props:
                cash_to_match -= board[useless_prop]['price']
                tmp_lst.append(useless_prop)
                if cash_to_match > 0:
                    continue
                else:
                    cash_req = abs(cash_to_match)
                    return 'T', 0, tmp_lst, cash_req, [id]

        # TODO: Trade reverse order preference of street class
        # Backup Strategy (taking care of debt by giving away useless props)
        if giveaway_props:
            tmp_lst = []
            cash_to_match = stateobj.debt
            for id in giveaway_props:
                # trying all combinations of useless prop and prop to offer
                cash_to_match -= board[id]['price']
                tmp_lst.append(id)
                if cash_to_match > 0:
                    continue
                else:
                    cash_req = abs(cash_to_match)
                    return 'T', 0, tmp_lst, cash_req, []

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
                # TODO : if lst_houses is empty launch fake deal
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

    def respondTrade(self, state):
        #Always reject the trade as you don;t want to lose your properties
        #TODO: prop value
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

