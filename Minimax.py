from turtle import st
from Board import *
from Agent import *
import time

class Minimax_Agent(Agent):
    def __init__(self, color, time_limit, local_search_method,
                local_search_init_args, local_search_run_args, 
                verbose=False):
        super().__init__(color, time_limit, local_search_method,
                        local_search_init_args, local_search_run_args)
        self.verbose = verbose
        self.neg_color = "brown" if color == "blue" else "blue"
        self.color_weight = {self.color: 1, self.neg_color: -1}

    # Implements Negamax (Minimax) algorithm.
    def get_choice(self, board):
        maximum = float('-inf')
        choice = None
        over = False
        start_time = time.process_time()
        depth_limit = 2

        # Call stack tuple arg_name -> position dictionary.
        id = {
                "cur_depth" : 0,
                "move"      : 1,
                "color"     : 2,
                "alpha"     : 3,
                "beta"      : 4,
                "value"     : 5,
                "parent_ptr": 6,
                "visited"   : 7,
                "saves"     : 8
            }

        while not over:
            # Negamax unrolled function call stack. (In order within tuple).
            #
            # @current depth, 
            # @move to apply (None for root).
            # @color of node 
            # @max - max value of current node.
            # @parent - reference to parent on the stack
            # @visited - marks if node is being visited for the first time. 
            # @saves - info needed to reverse apply a move.
            # 
            # Notes: 
            # - color is the color of the current node; but the current 
            # node performs the task of previous move application; this is a 
            # bit tricky but allows the board to be passed by reference (it's 
            # not even on the stack). 
            #
            # - parent reference is determined by the invariant that once 
            # a parent node is pushed onto the stack, it will remain at the 
            # same index while its children are being explored. 
            call_stack = [[0, [], self.color, float('-inf'), float('inf'), float('-inf'), 0, False, []]]
            while len(call_stack) > 0:
                if time.process_time() - start_time > self.time_limit:
                    over = True
                    break   
                # Get reference to location of current node. 
                cur_ptr = len(call_stack)-1
                # Pop node from the stack.
                [   cur_depth, 
                    move, 
                    color, 
                    alpha,
                    beta,
                    value, 
                    parent_ptr, 
                    visited, 
                    saves]        = call_stack.pop()
                # Negated color.
                #print(cur_depth, alpha)
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([0, [], color, alpha, beta, value, cur_ptr, True, []])
                        # Generate children of root node and push onto stack. 
                        for next_move in board.get_all_moves_ref(color):
                            call_stack.append([ 1, 
                                                next_move[:], 
                                                neg_color, 
                                                -beta,
                                                -alpha, 
                                                float('-inf'),
                                                cur_ptr,
                                                False,
                                                []])

                    # Otherwise we are done with current depth-limit 
                    # iteration. Update max. 
                    else:
                        if value > maximum:        
                            maximum = value
                            choice = move
                # Not at root node.
                else:
                    # If node hasn't been visited, apply move.
                    if not visited:
                        for piece_move in move:
                            save = board.apply_move_retState(piece_move[0], 
                                                             piece_move[1], 
                                                             neg_color)
                            saves.append(save)
                        # Check if at depth-limit or terminal node.
                        if board.game_over() or cur_depth == depth_limit:
                            if board.game_over():
                                if self.color == "brown" and board.brown_lost():
                                    value = self.color_weight[color] * -10.0
                                if self.color == "brown" and board.blue_lost():
                                    value = self.color_weight[color] * 10.0
                                if self.color == "blue" and board.blue_lost():
                                    value = self.color_weight[color] * -10.0
                                if self.color == "blue" and board.brown_lost():
                                    value = self.color_weight[color] * 10.0
                            else:
                                value = self.color_weight[color] * self.evaluate_node(board)
                            # Push terminal node back onto stack (with visited flag set).
                            call_stack.append([ cur_depth,
                                                move[:],
                                                color,
                                                alpha,
                                                beta,
                                                value, 
                                                parent_ptr,
                                                True,
                                                saves
                                              ])
                        # Otherwise generate children.
                        else:
                            # Push node back onto stack with visited flag set. 
                            call_stack.append([ cur_depth,
                                                move[:],
                                                color,
                                                alpha,
                                                beta, 
                                                value,
                                                parent_ptr,
                                                True,
                                                saves
                                              ])
                            # Generate children.
                            for next_move in board.get_all_moves_ref(color):
                                call_stack.append([ cur_depth+1, 
                                                    next_move[:], 
                                                    neg_color, 
                                                    -beta, 
                                                    -alpha,
                                                    float('-inf'),
                                                    parent_ptr,
                                                    False,
                                                    []])
                    # Otherwise node has been visited, undo moves and propagate values up. 
                    else:
                        for i in range(len(saves)-1, -1, -1):
                            board.reverse_apply_move(saves[i], neg_color)
                        if -value > call_stack[parent_ptr][id["value"]]:
                            call_stack[parent_ptr][id["value"]] = -value
                            if cur_depth == 1:
                                call_stack[parent_ptr][id["move"]] = move
                        if -value > call_stack[parent_ptr][id["alpha"]]:
                            call_stack[parent_ptr][id["alpha"]] = -value

                        if call_stack[parent_ptr][id["alpha"]] > call_stack[parent_ptr][id["beta"]]:
                            call_stack = call_stack[:parent_ptr+1]
                            continue
            # Increment depth limit (iterative deepening).
            break
        print(time.process_time() - start_time)
        return choice

    def enemy_royalty_count(self, counts):
        return (1 - (counts["king"] + counts["prince"] + counts["duke"])/3.0)
    
    def friendly_royalty_count(self, counts):
        return (counts["king"] + counts["prince"] + counts["duke"])/3.0

    def friendly_pieces_remaining(self,counts):
        res = 0.0
        res += counts["knight"]
        res += counts["sergeant"]
        res += counts["pikemen"]
        res += counts["squire"]
        res += counts["archer"]
        return (res / 10.0)

    def enemy_pieces_remaining(self, counts):
        res = 0.0
        res += counts["knight"]
        res += counts["sergeant"]
        res += counts["pikemen"]
        res += counts["squire"]
        res += counts["archer"]
        return 1 - (res / 10.0)

    def evaluate_node(self, board):
        if self.color == "brown":
            friendly_counts = board.brown_piece_counts
            enemy_counts = board.blue_piece_counts
        else:
            friendly_counts = board.blue_piece_counts
            enemy_counts = board.brown_piece_counts
        
        value = 0.0
        value += self.enemy_royalty_count(enemy_counts)
        value += self.friendly_royalty_count(friendly_counts)
        
        value += self.friendly_pieces_remaining(friendly_counts)
        value += self.enemy_pieces_remaining(enemy_counts)

        #value += self.in_enemy_castle(enemy_loc)
        return value

    