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
        # Make copy of current counts.
        current_counts = dict(board.get_counts(self.opponent_color))
        for moves in board.get_all_moves_ref(self.color):
            # Apply moves.
            saves = board.apply_moves(moves, self.color)
            if any_value_change(current_counts,
                board.get_counts(self.opponent_color)):
                return moves
            board.reverse_apply_moves(saves, self.color)
        # If no pure "greedy" move has been found, take a random action
        if chosen_move is None:
            return board.get_random_move(self.color)[0]

# Greedy w.r.t. "best" difference among enemy counts from start to result
# Simple preferences in order:
#   1. Eliminate as much royalty as possible
#   2. Eliminate as many enemy pieces as possible
#   3. Random move
class PieceGreedyRandomAgent(Agent):
    def get_choice(self, board):
        current_counts = dict(board.get_counts(self.opponent_color))
        some_royalty_eliminated = [] # Keep tuples of difference, move
        some_enemy_eliminated = [] # Keep tuples of difference, move
        for moves in board.get_all_moves_ref(self.color):
            # Apply sequence of moves to the board. 
            saves = board.apply_moves(moves, self.color)
            
            royalty_difference = any_value_change(current_counts,
                board.get_counts(self.opponent_color), ["king", "prince",
                "duke"])
            other_difference = any_value_change(current_counts,
                board.get_counts(self.opponent_color), ["knight",
                    "sergeant", "pikemen", "squire", "archer"])
            if royalty_difference:
                some_royalty_eliminated.append((moves, royalty_difference))
            if other_difference:
                some_enemy_eliminated.append((moves, other_difference))

            # Undo moves.
            board.reverse_apply_moves(saves, self.color)

        # For either royalty or enemy eliminated moves (in that priority order)
        # sort the lists by the difference associated with each move, then
        # take the last element (i.e. with greatest difference) and return it
        if len(some_royalty_eliminated) > 0:
            return sorted(some_royalty_eliminated, key=lambda x : x[1])[-1][0]
        elif len(some_enemy_eliminated) > 0:
            return sorted(some_enemy_eliminated, key=lambda x : x[1])[-1][0]
        else: # If no good move has been found, take a random action
            return board.get_random_move(self.color)[0]


