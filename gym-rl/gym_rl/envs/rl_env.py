import gym
from gym import error, spaces, utils
from gym.utils import seeding
import random
import constants

class RLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space= [0,0,0]
        self.q_table={}
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1
        self.PLAYER_TURN_INDEX = 0
        self.PROPERTY_STATUS_INDEX = 1
        self.PLAYER_POSITION_INDEX = 2
        self.PLAYER_CASH_INDEX = 3
        self.PHASE_NUMBER_INDEX = 4
        self.PHASE_PAYLOAD_INDEX = 5
        self.DEBT_INDEX = 6
        self.STATE_HISTORY_INDEX = 7
        self.penalties=0

    def reduceState(self, state):
        #perform state reduction

        return state

    def getStateFromQTable(self, state):
        #iterate q table and find the closest state to the state passed
        return state

    def updateState(self, state, cash, property):
        #perform state update
        return state

    def RLtraining(self, state, action_index):
        # get closest state from q table
        reduced_state = self.reduceState(state)
        if action_index==None:
            q_state = self.getStateFromQTable(reduced_state)
            max_q = max(self.q_table[q_state])
            action_index = self.q_table[q_state].index(max_q)

        next_state, reward = self.step(action_index, state)
        old_value = self.q_table[q_state]

        next_q_state = self.getStateFromQTable(next_state)
        next_max = max(self.q_table[next_q_state])

        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[q_state][action_index] = new_value
        return action_index
        # if reward == -10:
        #     self.penalties += 1
        #

    def step(self, action_index, state):
        # For plotting metrics
        #depending on action do deduction of amount or addition of amount
        next_state= self.updateState(state, state[self.PHASE_PAYLOAD_INDEX]["property"],
                                state[self.PHASE_PAYLOAD_INDEX]["cash"])

        reward= self.reward(next_state)
        return next_state, reward

    def reward(self, state):
        #calculate reward from state
        current_player = state[self.PLAYER_TURN_INDEX] % 2
        p = 2

        #smoothing factor
        c=0.1
        current_player_cash = state[self.PLAYER_CASH_INDEX][current_player]
        total_cash= state[self.PLAYER_CASH_INDEX][0] + state[self.PLAYER_CASH_INDEX][1]
        m = current_player_cash / total_cash

        #calculating value of all of current player's assets and the opponent player's assets
        assets_self=0
        assets_opp=0
        properties= state[self.PROPERTY_STATUS_INDEX]
        for i in range(len(properties)):
            if current_player == 0:
                if properties[i] < 0:
                    assets_self += constants.board[i]["price"]
                elif properties[i] > 0:
                    assets_opp += constants.board[i]["price"]
            else:
                if properties[i] > 0:
                    assets_self += constants.board[i]["price"]
                elif properties[i] < 0:
                    assets_opp += constants.board[i]["price"]
        v=  assets_self - assets_opp

        return ((v/p)*c)/(1+abs((v/p)*c)) + (m/p)

    def buyProperty(self, state):
        action_index = None
        reduced_state = self.reduceState(state)
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0,1)< 0.5:
                action_index=0
            else:
                action_index=2
        action_index= self.RLtraining(state, action_index)
        if action_index==0:
            return True
        return False

    def getBMST(self, state):
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            action_index= random.randrange(0, 3)
        action_index = self.RLtraining(state, action_index)
        if action_index == 0:
            return "B"
        if action_index == 1:
            return "S"
        return False

    def auctionProperty(self, state):
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0, 1) < 0.5:
                action_index = 0
            else:
                action_index = 2
        action_index = self.RLtraining(state, action_index)
        if action_index == 0:
            return True
        return False

    def respondTrade(self, state):
        action_index = None
        reduced_state = self.reduceState(state)
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            action_index = random.randrange(0, 3)
        action_index = self.RLtraining(state, action_index)
        #Either he is spending money or gaining money due to the trade then
        #In both cases Respond trade is true
        if action_index == 0 or action_index==1:
            return True
        return False

    def jailDecision(self, state):
        action_index = None
        reduced_state = self.reduceState(state)
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0, 1) < 0.5:
                action_index = 0
            else:
                action_index = -1
        action_index = self.RLtraining(state, action_index)
        #if he is willing to spend 50$
        if action_index == 0:
            return "P"
        #TODO: some logic to return "R" or "C"
        return "R"
