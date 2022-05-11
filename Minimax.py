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

    # Check time and update
    def update_time(self):                                              
        print(time.process_time())
        if time.process_time() - self.prev_time > self.time_limit:                       
            self.over = True                                                                                        
        self.prev_time = time.process_time()

    # Implements Negamax (Minimax) algorithm.
    def get_choice(self, board):
        maximum = float('-inf')
        choice = None
        over = False
        start_time = time.process_time()
        depth_limit = 1
        # Map from color to negation value. 
        

        # Call stack tuple arg_name -> position dictionary.
        id = {
                "cur_depth" : 0,
                "move"      : 1,
                "color"     : 2,
                "max_val"   : 3, 
                "parent_ptr": 4,
                "visited"   : 5,
                "saves"     : 6
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
            call_stack = [[0, [], self.color, -1.0, 0, False, []]]
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
                    max_val, 
                    parent_ptr, 
                    visited, 
                    saves]        = call_stack.pop()
                # Negated color.
                #print(cur_depth, max_val)
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([0, None, color, -1.0, None, True, []])
                        # Generate children of root node and push onto stack. 
                        for next_move in board.get_all_moves_ref(color):
                            call_stack.append([ 1, 
                                                next_move[:], 
                                                neg_color, 
                                                float('-inf'), 
                                                cur_ptr,
                                                False,
                                                []])

                    # Otherwise we are done with current depth-limit 
                    # iteration. Update max. 
                    else:
                        if max_val > maximum:         
                            maximum = max_val
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
                                max_val = self.color_weight[color] * 10.0
                            else:
                                max_val = self.color_weight[color] * self.evaluate_node(board)
                            # Push terminal node back onto stack (with visited flag set).
                            call_stack.append([ cur_depth,
                                                move[:],
                                                color,
                                                max_val, 
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
                                                max_val, 
                                                parent_ptr,
                                                True,
                                                saves
                                              ])
                            # Generate children.
                            for next_move in board.get_all_moves_ref(color):
                                call_stack.append([ cur_depth+1, 
                                                    next_move[:], 
                                                    neg_color, 
                                                    float('-inf'), 
                                                    cur_ptr,
                                                    False,
                                                    []])
                    # Otherwise node has been visited, undo moves and propagate values up. 
                    else:
                        for i in range(len(saves)-1, -1, -1):
                            board.reverse_apply_move(saves[i], neg_color)
                        if -max_val > call_stack[parent_ptr][id["max_val"]]:
                            call_stack[parent_ptr][id["max_val"]] = -max_val
                            if cur_depth == 1:
                                call_stack[parent_ptr][id["move"]] = move

            # Increment depth limit (iterative deepening).
            depth_limit += 1
        return choice

    def royalty_count(self, board, counts):
        return (1 - (counts["king"] + counts["prince"] + counts["duke"])/3.0)
    
    def pieces_remaining(self, board,counts):
        res = 0.0
        res += counts["knight"]
        res += counts["sergeant"]
        res += counts["pikemen"]
        res += counts["squire"]
        res += counts["archer"]

        return 1 - (res / 10.0)

    def evaluate_node(self, board):
        if self.color == "brown":
            counts = board.blue_piece_counts
        else:
            counts = board.brown_piece_counts
        
        value = 0.0
        value += self.royalty_count(board, counts)

        value += self.pieces_remaining(board,counts)

        return value

    