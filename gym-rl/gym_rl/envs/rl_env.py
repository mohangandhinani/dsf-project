import gym
import random
import constants

monopoly_lookup= {"Orange":0, "Pink":1, "Light Blue": 2,"Brown": 3, "Red": 4, "Yellow": 5, "Green": 6, "Dark Blue":7,"Railroad": 8, "Utility": 9}

class State(object):
    def __init__(self,state,my_id):
        self.player_id = my_id
        opponent_id = 2 if id==1 else 1
        self.turn = state[0]
        self.player_properties = state[1]
        self.my_position = state[2][my_id]
        self.opponent_position = state[2][opponent_id]
        self.my_cash = state[3][my_id]
        self.opponent_cash = state[3][opponent_id]
        self.phase = state[4]
        self.payload = state[5]
        self.debt = state[6]
        self.previous_states  = state[7]

class RLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space= [0,0,0]
        self.q_table={}
        #Q learning hyperparameters
        self.alpha = 0.1
        self.gamma = 0.6
        self.epsilon = 0.1

    def get_state_object(self,state):
        return State(state,self.id)

    def getFinanceFromState(self, state):
        print("Calculating finance vector")
        properties = state.player_properties

        self_propertyCount=0
        opp_propertyCount=0
        for i in range(len(properties)):
            if properties[i] != 0:  # Owned by someone
                if state.player_id == 1:
                    if properties[i] < 0:
                        self_propertyCount += 1
                    elif properties[i] > 0:
                        opp_propertyCount += 1
                else:
                    if properties[i] > 0:
                        self_propertyCount += 1
                    elif properties[i] < 0:
                        opp_propertyCount += 1
        print("selfproperty count:", self_propertyCount)
        print("oppproperty count:", opp_propertyCount)
        return (self_propertyCount / opp_propertyCount, (state.my_cash) / (1 + abs(state.my_cash)))

    def getPositionFromState(self, state):
        print("Calculating position vector")
        return state.my_position

    def getAreaFromState(self, state):
        print("Calculating area vector")
        area = [[0, 0] for i in range(10)]
        monopoly_size = [0 for i in range(10)]
        properties = state.player_properties

        for i in range(len(properties)):
            if properties[i] != 0: #Owned by someone
                property_object = constants.board[i]
                monopoly = property_object["monopoly"]
                if monopoly is not None:
                    monopoly_index = monopoly_lookup[monopoly]
                    if monopoly_size[monopoly_index] == 0:
                        monopoly_size[monopoly_index] = property_object["monopoly_size"]
                    if state.player_id == 1:
                        if properties[i] < 0:
                            area[0][monopoly_index] += 1
                        elif properties[i] > 0:
                            area[1][1] += 1
                    else:
                        if properties[i] > 0:
                            area[1][monopoly_index] += 1
                        elif properties[i] < 0:
                            area[0][monopoly_index] += 1
        print("Area:",area)
        for i in range(10):
            area[0][i] = area[0][i] / monopoly_size[i]
            area[1][i] = area[1][i] / monopoly_size[i]
        print("Area as %:", area)

    def reduceState(self, state):
        #perform state reduction
        print("Reducing state to q table state")

        area = self.getAreaFromState(state)
        position = self.getPositionFromState(state)
        finance = self.getFinanceFromState(state)

        print("finance:", finance)
        return (area, position, finance)

    def getStateFromQTable(self, state):
        #iterate q table and find the closest state to the state passed
        print("getting closest state from q table")
        area_1, position_1, finance_1 = state
        for s in self.q_table:
            print("checking against state:",s)
            area_2, position_2, finance_2 = s
            diff_area = 0
            for i in range(10):
                diff_area+= abs(area_1[0][i]-area_2[0][i]) + abs(area_1[1][i]-area_2[1][i])
                if diff_area > 0.1:
                    break
            diff_finance= abs(self.getFinanceFromState(state) - self.getFinanceFromState(s))
            diff_position= self.getPositionFromState(state)
            if diff_finance <= 0.1 and diff_position == 0 and diff_area <= 0.1 :
                print("found!.Returnng")
                return s
        print("Adding current state into q table")
        #TODO: discuss what to do here
        self.q_table[state] = [0,0,0]
        return state

    def RLtraining(self, id, state, action_index, type):
        # get closest state from q table
        reduced_state = self.reduceState(state)
        print("reduced state:", state," ## to state:",reduced_state)
        if action_index==None:
            q_state = self.getStateFromQTable(reduced_state)
            max_q = max(self.q_table[q_state])
            action_index = self.q_table[q_state].index(max_q)
        print("Identified action:",action_index)
        next_state, reward = self.step(action_index, state, reduced_state, type)
        old_value = self.q_table[q_state][action_index]

        next_q_state = self.getStateFromQTable(next_state)
        next_max = max(self.q_table[next_q_state])

        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[q_state][action_index] = new_value
        return action_index

    def step(self, action_index, state, q_state, type):
        print("updating state based on action")
        if type=="buy":
            property_number= state.payload["property_number"]
            if state.player_id ==1:
                state.player_properties[property_number] = 1
            else:
                state.player_properties[property_number] = -1
            state.my_cash-= state.payload["cash"]
            finance= self.getFinanceFromState(state)
            area= self.getAreaFromState(state)
            next_state = (area, state[1], finance)
        elif type=="auc":
            pass
        elif type=="build":
            property_number = state.payload["property_number"]
            state.my_cash -= constants.board[property_number]["build_cost"]
            if state.player_id ==1:
                state.player_properties[property_number] += 1
            else:
                state.player_properties[property_number] -= 1
            finance = self.getFinanceFromState(state)
            area= self.getAreaFromState(state)
            next_state = (area, state[1], finance)
        elif type=="sell":
            property_number = state.payload["property_number"]
            state.my_cash += constants.board[property_number]["build_cost"]
            if state.player_id ==1:
                state.player_properties[property_number] -= 1
            else:
                state.player_properties[property_number] += 1
            finance = self.getFinanceFromState(state)
            area= self.getAreaFromState(state)
            next_state = (area, state[1], finance)
        elif type=="mortgage":
            pass
        elif type=="unmortgage":
            pass
        elif type=="trade":
            property_number =state.payload["property_number"]
            state.my_cash += state.payload["cash"]
            finance = self.getFinanceFromState(state)
            if state.player_id ==1:
                state.player_properties[property_number] += 1
            else:
                state.player_properties[property_number] -= 1
            area= self.getAreaFromState(state)
            next_state = (area, state[1], finance)
        elif type=="jail" and action_index==0:
            state.my_cash -= 50
            finance = self.getFinanceFromState(state)
            next_state = (state[0], state[1], finance)
        else:
            next_state = state
        reward = self.reward(next_state)
        print("calculated reward:",reward)
        return next_state, reward

    def reward(self, state):
        #calculate reward from state
        p = 2

        #TODO: find right smoothing factor
        c=0.1

        current_player_cash = state.my_cash
        opponent_player_cash = state.opponent_cash
        m = current_player_cash / (current_player_cash + opponent_player_cash)

        assets_self=0
        assets_opp=0

        properties= state.player_properties
        for i in range(len(properties)):
            if properties[i] != 0: #Owned by someone
                price = constants.board[i]["price"]
                if state.player_id == 1:
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

    def buyProperty(self, id, state):
        state=self.get_state_object(state)
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            # "spend"= random true or false
            if random.uniform(0,1)< 0.5:
                action_index=0
            else:
                action_index=2
        action_index= self.RLtraining(id, state, action_index, "buy")
        if action_index==0:
            return True
        return False

    def getBMST(self, id, state):
        state= self.get_state_object(state)
        action_index = None
        if random.uniform(0, 1) < self.epsilon:
            action_index= random.randrange(0, 3)
        action_index = self.RLtraining(id, state, action_index,"BMST")
        if action_index == 0:
            return ("B",[])
        if action_index == 1:
            return ("S",[])
        return False

    def auctionProperty(self, id, state):
        state = self.get_state_object(state)
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

    def respondTrade(self, id, state):
        state = self.get_state_object(state)
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

    def jailDecision(self, id, state):
        state = self.get_state_object(state)
        action_index = None
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

