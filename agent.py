#TO DO : timeout decorator

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
        self.debt = state[6]
        self.previous_states  = state[7]

class Agent(object):
    def __init__(self, id=0):
        self.id = id  # Player 1 -> id=1, Player 2 ->id=2

    def get_state_object(self,state):
        return State(state,self.id)

    def getBMSTDecision(self, state):
        pass

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

