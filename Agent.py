from LocalSearch import *

local_search_agents = {
    "HillClimbingGreedy" : HillClimbingGreedy,
    "HillClimbingFirstChoice" : HillClimbingFirstChoice,
    "SimulatedAnnealing" : SimulatedAnnealing
}

class Agent():
    # How to handle variable arguments
    def __init__(self, color, time_limit, local_search_method,
        local_search_init_args, local_search_run_args):
        self.color = color
        self.time_limit = time_limit
        self.local_search_method = local_search_agents[
            local_search_method](**local_search_init_args)
        self.local_search_run_args = local_search_run_args # Dictionary

    # @return   A list of (origin, new location) pairs
    def get_choice(self, board):
        pass

    def get_piece_placement(self, board):
        return self.local_search_method.get_piece_placement(
            **self.local_search_run_args)

    def get_statistics(self):
        pass

class HumanAgent(Agent):
    def get_choice(self, board):
        pass

class RandomAgent(Agent):
    def get_choice(self, board):
        return board.get_random_move(self.color)[0]
