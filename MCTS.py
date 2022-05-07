# Module for all MCTS based Agents

# NOTE: The implementation of the Node and MCTS_UCT_Agent classes is inspired
#       by pseudocode and explanation from the following sources:
#       - Russell, Stuart, and Peter Norvig. Artificial Intelligence:
#           A Modern Approach, 4th edition. (Hoboken: Pearson, 2021).
#           [In particular, Chapter 5, section 5.4]
#       - Browne, C. Powley, E. J., Whitehouse D., Lucas, S. M.,
#           Cowling, P. I., Rohlfshagen, P., Tavener, S., Liebana, D. P.,
#           Samothrakis, S., and Colton, S..
#           “A survey of Monte Carlo tree search methods.”
#           IEEE Transactions on Computational Intelligence and AI in Games, 4
#           (2012), 1-43.

import math
from time import process_time
from Agent import *
from GameExecution import *

# Node class to be used in the constructed search tree
class Node():
    # @param state          A representation of the state. For now the
    #                       assumption is that state is an instance of Board
    # @param parent         Another instance of Node that is the parent of this
    #                       Node in the search tree
    # @param action         The action that led from the parent state to this
    #                       state -> a list of (origin, new location) tuples
    # @param depth          The depth of the node in the search tree
    # @param color          The color of the player whose turn it is in this
    #                       state
    # @param utility        The number of wins (utility) for this Node;
    #                       default 0 but made an init argument in case a
    #                       a method which uses some other initializaiton is
    #                       used
    # @param num_playouts   The number of playouts that have gone through this
    #                       Node; default 0, made an argument for the same
    #                       reason as utility
    def __init__(self, state, parent, action, depth, color, utility=0,
        num_playouts=0):
        self.state = state
        self.parent = parent
        self.children = []
        self.action = action
        self.depth = depth
        self.color = color
        self.utility = utility
        self.num_playouts = num_playouts
        self.num_children = 0
        self.num_possible_children = state.get_num_all_moves(color)
        self.actions_tried = set()

    def is_fully_expanded(self):
        return self.num_children == self.num_possible_children

    def is_terminal(self):
        return self.state.game_over()

# A lightweight version of regular Agents
class PlayoutAgent():
    def __init__(self, color):
        self.color = color

# A lightweight version of the RandomAgent
# NOTE: Given the usage of Board's get_random_move function, this is not a
#       uniform random action agent - if it were, it would be extremely biased
#       towards multiple piece moves; using the method it does, it is actually
#       biased towards better gameplay, where every move need not involve all
#       pieces
class RandomPlayoutAgent(PlayoutAgent):
    def get_choice(self, board):
        return board.get_random_move(self.color)[0]

playout_dict = {
    "random" : RandomPlayoutAgent
}

class MCTS_UCT_Agent(Agent):
    # All parameters are the same as Agent with the exception of...
    # @param c                      The exploration term (C) in the UCT formula
    # @param playout_class          The type (given as a string) of playout to
    #                               use, such as "random"
    # @param playout_class_args     A dictionary of arguments, if any, to pass
    #                               to the playout agent
    def __init__(self, color, time_limit, local_search_method,
        local_search_init_args, local_search_run_args, c, playout_class,
        playout_class_args=dict(), verbose=False):
        super().__init__(color, time_limit, local_search_method,
            local_search_init_args, local_search_run_args)
        self.c = c
        self.safe_limit = .9 * self.time_limit
        self.verbose = verbose

        # Setup playout agents
        playout_class_args["color"] = "blue"
        self.playout_blue = playout_dict[playout_class](**playout_class_args)
        playout_class_args["color"] = "brown"
        self.playout_brown = playout_dict[playout_class](**playout_class_args)

        # Statistics tracking
        self.num_simulations = []
        self.max_depths = []

    # The function for running MCTS
    def get_choice(self, board):
        # Start a clock to ensure an answer is given within the time limit
        start_time = process_time()
        # Start tracking number of simulations and max depth
        number_of_sims = 0
        max_depth = 0

        # Initialize the tree
        tree = Node(board.clone(), None, None, 0, self.color, 0, 0)

        # While there is remaining time, run the following four steps:
        # 1. select, 2. expand, 3. simulate, and 4. backpropagate
        # While checking for running out of time at any point in the loop
        while (process_time() - start_time < self.safe_limit):
            selected = self.select(tree, start_time)
            if selected is None:
                break
            child = self.expand(selected, start_time)
            if child is None:
                break
            if child.depth > max_depth:
                max_depth = child.depth
            result = self.simulate(child, start_time)
            if result is None:
                break
            number_of_sims += 1
            if not self.back_propagate(result, child, start_time):
                break

        # Update stats from this decision
        self.num_simulations.append(number_of_sims)
        self.max_depths.append(max_depth)

        if self.verbose:
            print("Number of simulations:", number_of_sims)
            print("Max search depth:", max_depth)

        # Return best move
        best_child = self.best_child(tree, 0)
        return best_child.action

    # Finds the "best child" either in the select phase of the algorithm or for
    # returning the final move, where the c (exploration multiplier) should be
    # set to 0
    def best_child(self, node, c):
        if 1 == node.num_children:
            return node.children[0]
        else:
            first_child = node.children[0]
            max_node = first_child
            max_value = (first_child.utility / max(1,first_child.num_playouts)) + \
                (c * math.sqrt(
                    (2 * math.log(node.num_playouts)) / \
                    (max(1,first_child.num_playouts))))
            for child in node.children[1:]:
                value = (child.utility / max(1, child.num_playouts)) + \
                    (c * math.sqrt(
                        (2 * math.log(node.num_playouts)) / \
                        (max(1,child.num_playouts))))

                if value > max_value:
                    max_value = value
                    max_node = child

            return max_node


    def select(self, node, start_time):
        curr_node = node
        while not curr_node.is_terminal():
            if (process_time() - start_time > self.safe_limit):
                return None

            if not curr_node.is_fully_expanded():
                return curr_node
            else:
                curr_node = self.best_child(curr_node, self.c)

        return curr_node

    # Per the Browne et al. paper, this uses "random" expansion - however, as
    # noted elsewhere, get_random_move does not return all moves with uniform
    # random probability - for the purposes of expansion though this is
    # is probably for the best, as otherwise the vast majority of expansion
    # would only be for the moves that involve moving as many pieces as
    # allowed
    def expand(self, node, start_time):
        if (process_time() - start_time > self.safe_limit):
            return None

        # Choose a random action and get a new state
        random_action, new_board = node.state.get_random_move(node.color)
        # If action has already been tried, get a new one
        while (tuple(random_action) in node.actions_tried):
            random_action, new_board = node.state.get_random_move(node.color)

        # Prepare node for that state
        # First the color (i.e. whose turn it is) should be the opposite of the
        # parent
        new_color = "blue" if node.color == "brown" else "brown"
        new_node = Node(state=new_board, parent=node, action=random_action,
            depth=(node.depth + 1), color=new_color, utility=0, num_playouts=0)

        # Handle the bookkeeping for the parent
        node.children.append(new_node)
        node.num_children += 1
        node.actions_tried.add(tuple(random_action))

        return new_node

    # Simulate a run of the game from the newly added child node
    def simulate(self, child, start_time):
        if (process_time() - start_time > self.safe_limit):
            return None

        blue_turn = True if "blue" == child.color else False
        winner = run_game_simulation(child.state.clone(),
            self.playout_blue, self.playout_brown, blue_turn,
            start_time, self.safe_limit)

        if winner is None:
            return winner

        return 1 if child.color == winner else 0

    # As this function operates on the tree in place, it returns False if it
    # had to abort because of no more time, else True for success
    def back_propagate(self, result, child, start_time):
        curr_node = child
        curr_result = result
        while curr_node is not None:
            if (process_time() - start_time > self.safe_limit):
                return False
            curr_node.num_playouts += 1
            curr_node.utility += curr_result
            curr_result = 1 - curr_result # Flip the result
            curr_node = curr_node.parent # Step up to parent

        return True




