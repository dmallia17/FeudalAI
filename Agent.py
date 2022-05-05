

class Agent():
    # How to handle variable arguments
    def __init__(self, color, time_limit):
        self.color = color
        self.time_limit = time_limit

    # @return   A list of (origin, new location) pairs
    def get_choice(self, board):
        pass

class HumanAgent(Agent):
    def get_choice(self, board):
        pass

class RandomAgent(Agent):
    def get_choice(self, board):
        return board.get_random_move(self.color)[0]
