import gym
from gym import error, spaces, utils
from gym.utils import seeding
import random
import constants

monopoly_lookup= {"Orange":0, "Pink":1, "Light Blue": 2,"Brown": 3, "Red": 4, "Yellow": 5, "Green": 6, "Dark Blue":7,"Railroad": 8, "Utility": 9}
class RLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space= [0,0,0]
        self.q_table={}

        #Q learning hyperparameters
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1

        #For looking up values in the state
        self.PLAYER_TURN_INDEX = 0
        self.PROPERTY_STATUS_INDEX = 1
        self.PLAYER_POSITION_INDEX = 2
        self.PLAYER_CASH_INDEX = 3
        self.PHASE_NUMBER_INDEX = 4
        self.PHASE_PAYLOAD_INDEX = 5
        self.DEBT_INDEX = 6
        self.STATE_HISTORY_INDEX = 7

        self.CHANCE_GET_OUT_OF_JAIL_FREE = 40
        self.COMMUNITY_GET_OUT_OF_JAIL_FREE = 41

        self.penalties=0
        self.assets_self = 0
        self.assets_opp = 0

        self.current_player_cash =0
        self.opponent_player_cash =0

    def getFinanceFromState(self, state, current_player):
        current_player_cash = state[self.PLAYER_CASH_INDEX][current_player]
        properties = state[self.PROPERTY_STATUS_INDEX]

        self_propertyCount=0
        opp_propertyCount=0
        for i in range(len(properties)):
            if properties[i] != 0:  # Owned by someone
                if current_player == 0:
                    if properties[i] < 0:
                        self_propertyCount += 1
                    elif properties[i] > 0:
                        opp_propertyCount += 1
                else:
                    if properties[i] > 0:
                        self_propertyCount += 1
                    elif properties[i] < 0:
                        opp_propertyCount += 1
        return (self_propertyCount / opp_propertyCount, (current_player_cash) / (1 + abs(current_player_cash)))

    def getPositionFromState(self, state, current_player):
        return state[self.PLAYER_POSITION_INDEX][current_player]

    def getAreaFromState(self, state, current_player):
        area = [[0, 0] for i in range(10)]
        monopoly_size = [0 for i in range(10)]
        properties = state[self.PROPERTY_STATUS_INDEX]

        for i in range(len(properties)):
            if properties[i] != 0: #Owned by someone
                property_object = constants.board[i]
                monopoly = property_object["monopoly"]
                if monopoly is not None:
                    monopoly_index = monopoly_lookup[monopoly]
                    if monopoly_size[monopoly_index] == 0:
                        monopoly_size[monopoly_index] = property_object["monopoly_size"]
                    if current_player == 0:
                        if properties[i] < 0:
                            area[0][monopoly_index] += 1
                        elif properties[i] > 0:
                            area[1][1] += 1
                    else:
                        if properties[i] > 0:
                            area[1][monopoly_index] += 1
                        elif properties[i] < 0:
                            area[0][monopoly_index] += 1
        for i in range(10):
            area[0][i] = area[0][i] / monopoly_size[i]
            area[1][i] = area[1][i] / monopoly_size[i]

    def reduceState(self, state):
        #perform state reduction
        current_player = state[self.PLAYER_TURN_INDEX] % 2

        self.current_player_cash = state[self.PLAYER_CASH_INDEX][current_player]
        self.opponent_player_cash = state[self.PLAYER_CASH_INDEX][abs(current_player - 1)]
        area = self.getAreaFromState(state, current_player)
        position = self.getPositionFromState(state, current_player)
        finance = self.getFinanceFromState(state, current_player)

        return (area, position, finance)

    def getStateFromQTable(self, state):
        #iterate q table and find the closest state to the state passed
        area_1, position_1, finance_1 = state
        current_player = state[self.PLAYER_TURN_INDEX] % 2
        for s in self.q_table:
            area_2, position_2, finance_2 = s
            diff_area = 0
            for i in range(10):
                diff_area+= abs(area_1[0][i]-area_2[0][i]) + abs(area_1[1][i]-area_2[1][i])
                if diff_area > 0.1:
                    break
            diff_finance= abs(self.getFinanceFromState(state, current_player) - self.getFinanceFromState(s, current_player))
            diff_position= self.getPositionFromState(state, current_player)
            if diff_finance <= 0.1 and diff_position == 0 and diff_area <= 0.1 :
                return s

        #TODO: dicuss what to do here
        self.q_table[state] = [0,0,0]
        return state

    def RLtraining(self, state, action_index, type):
        # get closest state from q table
        reduced_state = self.reduceState(state)
        if action_index==None:
            q_state = self.getStateFromQTable(reduced_state)
            max_q = max(self.q_table[q_state])
            action_index = self.q_table[q_state].index(max_q)

        next_state, reward = self.step(action_index, reduced_state, type, state[self.PLAYER_TURN_INDEX]%2)
        old_value = self.q_table[q_state][action_index]

        next_q_state = self.getStateFromQTable(next_state)
        next_max = max(self.q_table[next_q_state])

        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[q_state][action_index] = new_value
        return action_index

    def step(self, action_index, state, type, current_player):
        if type=="buy":
            property_number= state[self.PHASE_PAYLOAD_INDEX]["property_number"]
            if current_player ==0:
                state[self.PROPERTY_STATUS_INDEX][property_number] = 1
            else:
                state[self.PROPERTY_STATUS_INDEX][property_number] = -1
            state[self.PLAYER_CASH_INDEX][current_player]-= state[self.PHASE_PAYLOAD_INDEX]["cash"]
            finance= self.getFinanceFromState(state, current_player)
            area= self.getAreaFromState(state, current_player)
            next_state = (area, state[1], finance)
        elif type=="auc":
            pass
        elif type=="build":
            property_number = state[self.PLAYER_POSITION_INDEX]
            state[self.PLAYER_CASH_INDEX][current_player] -= constants.board[property_number]["build_cost"]
            finance = self.getFinanceFromState(state, current_player)
            if current_player ==0:
                state[self.PROPERTY_STATUS_INDEX][property_number] += 1
            else:
                state[self.PROPERTY_STATUS_INDEX][property_number] -= 1
            area= self.getAreaFromState(state, current_player)
            next_state = (area, state[1], finance)
        elif type=="sell":
            property_number = state[self.PLAYER_POSITION_INDEX]
            state[self.PLAYER_CASH_INDEX][current_player] += constants.board[property_number]["build_cost"]
            finance = self.getFinanceFromState(state, current_player)
            if current_player ==0:
                state[self.PROPERTY_STATUS_INDEX][property_number] -= 1
            else:
                state[self.PROPERTY_STATUS_INDEX][property_number] += 1
            area= self.getAreaFromState(state, current_player)
            next_state = (area, state[1], finance)
        elif type=="mortgage":
            pass
        elif type=="unmortgage":
            pass
        elif type=="trade":
            property_number = state[self.PLAYER_POSITION_INDEX]
            state[self.PLAYER_CASH_INDEX][current_player] -= state[self.PHASE_PAYLOAD_INDEX]["cash"]
            finance = self.getFinanceFromState(state, current_player)
            if current_player ==0:
                state[self.PROPERTY_STATUS_INDEX][property_number] += 1
            else:
                state[self.PROPERTY_STATUS_INDEX][property_number] -= 1
            area= self.getAreaFromState(state, current_player)
            next_state = (area, state[1], finance)
        elif type=="jail" and action_index==0:
            state[self.PLAYER_CASH_INDEX][current_player] -= 50
            finance = self.getFinanceFromState(state, current_player)
            next_state = (state[0], state[1], finance)
        else:
            next_state = state
        reward = self.reward(next_state, current_player)
        return next_state, reward

    def reward(self, state, current_player):
        #calculate reward from state
        p = 2

        #TODO: find right smoothing factor
        c=0.1

        current_player_cash = state[self.PLAYER_CASH_INDEX][current_player]
        opponent_player_cash = state[self.PLAYER_CASH_INDEX][abs(current_player-1)]
        m = current_player_cash / (current_player_cash + opponent_player_cash)

        assets_self=0
        assets_opp=0

        properties= state[self.PROPERTY_STATUS_INDEX]
        for i in range(len(properties)):
            if properties[i] != 0: #Owned by someone
                price = constants.board[i]["price"]
                if current_player == 0:
                    if properties[i] < 0:
                        assets_self += price
                    elif properties[i] > 0:
                        assets_opp += price
                else:
                    if properties[i] > 0:
                        assets_self += price
                    elif properties[i] < 0:
                        assets_opp += price
        v=  assets_self - assets_opp

        return ((v/p)*c)/(1+abs((v/p)*c)) + (m/p)

    def buyProperty(self, state):
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0,1)< 0.5:
                action_index=0
            else:
                action_index=2
        action_index= self.RLtraining(state, action_index, "buy")
        if action_index==0:
            return True
        return False

    def getBMST(self, state):
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            action_index= random.randrange(0, 3)
        action_index = self.RLtraining(state, action_index,"BMST")
        if action_index == 0:
            return ("B",[])
        if action_index == 1:
            return ("S",[])
        return False

    def auctionProperty(self, state):
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0, 1) < 0.5:
                action_index = 0
            else:
                action_index = 2
        action_index = self.RLtraining(state, action_index,"auc")
        if action_index == 0:
            return True
        return False

    def respondTrade(self, state):
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            action_index = random.randrange(0, 3)
        action_index = self.RLtraining(state, action_index, "resp_trade")
        #Either he is spending money or gaining money due to the trade
        #In both cases Respond trade is true
        if action_index == 0 or action_index==1:
            return True
        return False

    def jailDecision(self, state):
        action_index = None
        current_player = state[self.PLAYER_TURN_INDEX] % 2
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0, 1) < 0.5:
                action_index = 0
            else:
                action_index = -1
        action_index = self.RLtraining(state, action_index,"jail")
        #if he is willing to spend 50$
        if action_index == 0:
            return "P"
        elif state[self.CHANCE_GET_OUT_OF_JAIL_FREE] in (-1,1):
            return ("C", self.CHANCE_GET_OUT_OF_JAIL_FREE)
        elif state[self.COMMUNITY_GET_OUT_OF_JAIL_FREE] in (-1, 1):
            return ("C", self.COMMUNITY_GET_OUT_OF_JAIL_FREE)
        else:
            return "R"

