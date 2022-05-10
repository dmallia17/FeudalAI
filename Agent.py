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
        self.opponent_color = "blue" if self.color == "brown" else "brown"
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

# @param dict1      INITIAL dictionary (i.e. start state)
# @param dict2      RESULT dictionary (i.e. result state)
# @param keys       Optional list of keys of interest
def any_value_change(dict1, dict2, keys=list()):
    check_keys = keys if len(keys) > 0 else list(dict1.keys())
    difference = 0
    for k in check_keys:
        difference += dict1[k] - dict2[k]
    return difference

class PureGreedyRandomAgent(Agent):
    def get_choice(self, board):
        chosen_move = None
        current_counts = board.get_counts(self.opponent_color)
        for (move, new_board) in board.get_all_moves(self.color):
            if any_value_change(current_counts,
                new_board.get_counts(self.opponent_color)):
                return move
        # If no pure "greedy" move has been found, take a random action
        if chosen_move is None:
            return board.get_random_move(self.color)[0]

# Greedy w.r.t. greatest difference
class TargetedGreedyRandomAgent(Agent):
    def get_choice(self, board):
        pass
