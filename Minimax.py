# Module for minimax implementations.
# As of now, the choice of minimax agent to run is 
# hard coded in the get_choice function (This should be modified so that
# it can be placed in a config). 

import random
from Board import *
from Agent import *
import time
from Heuristics import *

LT, EQ, GT = -1,0,1

class Minimax_Agent(Agent):
    def __init__(self, color, time_limit, local_search_method,
                local_search_init_args, local_search_run_args, 
                verbose=False):
        super().__init__(color, time_limit, local_search_method,
                        local_search_init_args, local_search_run_args)
        self.verbose = verbose
        self.neg_color = "brown" if color == "blue" else "blue"
        self.color_weight = {self.color: 1, self.neg_color: -1}
        self.tt = {}
        self.time_limit = .9 * time_limit

        # Statistics
        self.max_depth = []
        self.nodes_reached = []
        self.nodes_expanded = []
        self.nodes_pruned = []
        self.transposition_hits = []

    def get_statistics(self):
        return {
            "max depth"         : self.max_depth[:],
            "nodes reached"     : self.nodes_reached[:],
            "nodes expanded"    : self.nodes_expanded[:],
            "nodes pruned"      : self.nodes_pruned[:],
            "TT hits"           : self.transposition_hits[:]
        }

    # Returns choice using certain negamax algorithm.
    def get_choice(self, board):
        self.start_time = time.process_time()
        self.tt = {}
        return self.negamax_with_mem(board)
        #return self.iter_deepening(board)


    # Implements Negamax (Minimax) algorithm.
    # This is the basic negamax with alpha beta pruning stack framework 
    # which all the other enhancements derive from. 
    # Although this is "code bloat", in a sense, it was easier to keep them separate
    # For efficiency purposes, and for allowing to work and modify each implementation as 
    # necessary, given the details of a certain algorithm.
    def negamax(self, board):
        maximum = float('-inf')
        choice = []
        over = False
        depth_limit = 1
        nodes_pruned = 0
        max_depth = 0

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
            # @alpha - alpha bound
            # @beta - beta bound
            # @value - calculated value of node
            # @parent_ptr - reference to parent on the stack
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
                if time.process_time() - self.start_time > self.time_limit:
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
                if cur_depth > max_depth:
                    max_depth = cur_depth
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([0, [], color, alpha, beta, value, cur_ptr, True, []])
                        # Generate children of root node and push onto stack. 
                        
                        
                        #cluster = {}

                        for next_move in board.get_all_moves_ref(color):
                            # Check if next move is a win. 
                            saves = board.apply_moves(next_move, self.color)
                            if board.game_over():
                                if self.color == "blue":
                                    if board.brown_lost():
                                        return next_move
                                else:
                                    if board.blue_lost():
                                        return next_move

                            # v = self.color_weight[color] * self.evaluate_node(board)

                            # if v not in cluster:
                            #     cluster[v] = [next_move]
                            # else:
                            #     cluster[v].append(next_move)

                            board.reverse_apply_moves(saves, color)

                        # for k,v in sorted(cluster.items()):
                            call_stack.append([ 1, 
                                                #random.choice(cluster[k]),
                                                next_move,
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
                            #cluster = {}
                            for next_move in board.get_all_moves_ref(color):
                                saves = board.apply_moves(next_move, color)
                                # v = self.color_weight[color] * self.evaluate_node(board)

                                # if v not in cluster:
                                #     cluster[v] = [next_move]
                                # else:
                                #     cluster[v].append(next_move)

                                board.reverse_apply_moves(saves, color)



                            # for k,v in sorted(cluster.items()):
                                call_stack.append([ cur_depth+1, 
                                                    #random.choice(cluster[k]),
                                                    next_move[:],
                                                    neg_color, 
                                                    -beta, 
                                                    -alpha,
                                                    float('-inf'),
                                                    cur_ptr,
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
                            for i in range(parent_ptr, cur_ptr):
                                call_stack[i][id["alpha"]] = -value
                        if call_stack[parent_ptr][id["alpha"]] >= call_stack[parent_ptr][id["beta"]]:
                            nodes_pruned += (len(call_stack) - parent_ptr)
                            call_stack = call_stack[:parent_ptr+1]
            # Increment depth limit (iterative deepening).
            depth_limit += 1 
        print("NODES PRUNED:", nodes_pruned)
        print("MAX DEPTH REACHED:", max_depth)
        return choice



    # This is basic negamax with alpha beta pruning and transposition table implementation. 
    # The framework is the same as the negamax implementation, but transposition table logic 
    # is derived from Dennis Breuker's PhD thesis, "Memory versus search in games" (1998), p. 16-18
    def negamax_with_mem(self, board):
        
        maximum = float('-inf')
        choice = []
        over = False
        nodes_reached = 0
        nodes_expanded = 0
        nodes_pruned = 0
        transposition_hits = 0
        depth_limit = 1
        max_depth = 0
        
        # Transposition Table
        tt = {}
        
        # Call stack tuple arg_name -> position dictionary.
        id = {
                "cur_depth" : 0,
                "move"      : 1,
                "color"     : 2,
                "alpha"     : 3,
                "beta"      : 4,
                "value"     : 5,
                "alpha_orig": 6,
                "parent_ptr": 7,
                "visited"   : 8,
                "saves"     : 9
            }

        while not over:
            call_stack = [[0, [], self.color, float('-inf'), float('+inf'), float('-inf'), float('-inf'), 0, False, []]]
            while len(call_stack) > 0:
                if time.process_time() - self.start_time > self.time_limit:
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
                    alpha_orig, 
                    parent_ptr, 
                    visited, 
                    saves]        = call_stack.pop()
                max_depth = max(cur_depth, max_depth)
                # Negated color.
                neg_color = "brown" if color == "blue" else "blue"
                max_depth = max(cur_depth, max_depth)
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([ 0, 
                                            [], 
                                            color, 
                                            alpha, 
                                            beta, 
                                            value, 
                                            alpha_orig, 
                                            cur_ptr, 
                                            True, 
                                            []])
                        nodes_expanded += 1
                        # Generate children of root node and push onto stack. 
                        for next_move in board.get_all_moves_ref(color):
                            nodes_reached += 1
                            call_stack.append([ 1, 
                                                next_move[:], 
                                                neg_color, 
                                                -beta,
                                                -alpha, 
                                                float('-inf'),
                                                -beta,
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

                        # Check transposition table for depth >= 2. 
                        if cur_depth >= 1:
                            key = board.get_hash_key()
                            if key in tt and tt[key]['depth'] >= depth_limit - cur_depth:
                                tt_entry = tt[key]
                                v = tt_entry['value']
                                transposition_hits += 1
                                if tt_entry['flag'] == EQ:
                                    # return tt_entry value
                                    for i in range(len(saves)-1, -1, -1):
                                        board.reverse_apply_move(saves[i], neg_color)
                                    if -v > call_stack[parent_ptr][id["value"]]:
                                        call_stack[parent_ptr][id["value"]] = -v
                                        if cur_depth == 1:
                                            call_stack[parent_ptr][id["move"]] = move
                                    if -v > call_stack[parent_ptr][id["alpha"]]:
                                        call_stack[parent_ptr][id["alpha"]] = -v
                                    for i in range(parent_ptr, cur_ptr):
                                        call_stack[i][id["alpha"]] = -v
                                    continue
                                elif tt_entry['flag'] == LT:
                                    alpha = max(alpha, v)
                                elif tt_entry['flag'] == GT:
                                    beta = min(beta, v)

                                if alpha >= beta:
                                    v = tt_entry['value']
                                    # return tt_entry value
                                    for i in range(len(saves)-1, -1, -1):
                                        board.reverse_apply_move(saves[i], neg_color)
                                    if -v > call_stack[parent_ptr][id["value"]]:
                                        call_stack[parent_ptr][id["value"]] = -v
                                        if cur_depth == 1:
                                            call_stack[parent_ptr][id["move"]] = move
                                    if -v > call_stack[parent_ptr][id["alpha"]]:
                                        call_stack[parent_ptr][id["alpha"]] = -v
                                    for i in range(parent_ptr, cur_ptr):
                                        call_stack[i][id["alpha"]] = -v
                                    continue

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
                                                alpha_orig,
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
                                                alpha_orig,
                                                parent_ptr,
                                                True,
                                                saves
                                              ])
                            # Generate children.
                            nodes_expanded += 1
                            for next_move in board.get_all_moves_ref(color):
                                nodes_reached += 1
                                call_stack.append([ cur_depth+1, 
                                                    next_move[:], 
                                                    neg_color, 
                                                    -beta, 
                                                    -alpha,
                                                    float('-inf'),
                                                    -beta,
                                                    cur_ptr,
                                                    False,
                                                    []])
                    # Otherwise node has been visited, undo moves and propagate values up. 
                    else:

                        # Get hash key for current board.
                        hash_key = board.get_hash_key()

                        for i in range(len(saves)-1, -1, -1):
                            board.reverse_apply_move(saves[i], neg_color)
                        if -value > call_stack[parent_ptr][id["value"]]:
                            call_stack[parent_ptr][id["value"]] = -value
                            if cur_depth == 1:
                                call_stack[parent_ptr][id["move"]] = move
                        if -value > call_stack[parent_ptr][id["alpha"]]:
                            call_stack[parent_ptr][id["alpha"]] = -value
                            for i in range(parent_ptr, cur_ptr):
                                call_stack[i][id["alpha"]] = -value
                        if call_stack[parent_ptr][id["alpha"]] >= call_stack[parent_ptr][id["beta"]]:
                            nodes_pruned += (len(call_stack) - parent_ptr)
                            call_stack = call_stack[:parent_ptr+1]
                            continue
                            

                        # Transposition table caching happens here. 
                        mem = {}
                        mem['value'] = value
                        if value <= alpha_orig:
                            mem['flag'] = GT
                        elif value >= beta:
                            mem['flag'] = LT
                        else:
                            mem['flag'] = EQ
                        mem['depth'] = depth_limit - cur_depth
                        tt[hash_key] = mem
            depth_limit += 1
        
        if self.verbose:
            print("MAX DEPTH", max_depth)
            print("NODES REACHED", nodes_reached)
            print("NODES EXPANDED", nodes_expanded)
            print("NODES PRUNED:", nodes_pruned)
            print("TRANSPOSITION HITS", transposition_hits)
            print("MAX DEPTH", max_depth)

        self.max_depth.append(max_depth)
        self.nodes_reached.append(nodes_reached)
        self.nodes_expanded.append(nodes_expanded)
        self.nodes_pruned.append(nodes_pruned)
        self.transposition_hits.append(transposition_hits)

        return choice


    # Iterative deepening for MTD(f). 
    def iter_deepening(self, board):
        value_guess = 0
        for depth in range(1,4):
            (choice, value_guess) = self.MTD_F(board, value_guess, depth)
            print(depth)
            if time.process_time() - self.start_time > self.time_limit:
                break
        return choice

    # MTD-F Algorithm from the paper, 
    # Plaat, Aske, Jonathan Schaeffer, Wim Pijls and Arie de Bruin. “A New Paradigm for Minimax Search.” ArXivLabs/1404.1515 (2014)
    # One of the authors, Aske Plaat, has a web-page with some simple psuedocode and notes regarding the algorithm: 
    # https://askeplaat.wordpress.com/534-2/mtdf-algorithm/
    def MTD_F(self, board, value_guess, max_depth):
        upper_bound = float('inf')
        lower_bound = float('-inf')

        while lower_bound < upper_bound:
            if value_guess == lower_bound:
                beta = value_guess + 1
            else:
                beta = value_guess
            (choice, value_guess) = self.negamax_with_mem_MTD_F(board, beta-1, beta, max_depth)
            if value_guess < beta:
                upper_bound = value_guess
            else:
                lower_bound = value_guess
        
        return (choice, value_guess)

    # This is the same as the base negamax implementation but modified to work with MTD-F (i.e., it only goes to 
    # a certain depth limit on one iteration.)
    def negamax_with_mem_MTD_F(self, board, alpha, beta, depth_limit):
        
        maximum = float('-inf')
        choice = []
        over = False
        nodes_reached = 0
        nodes_expanded = 0
        nodes_pruned = 0
        transposition_hits = 0
        tt = self.tt

        # Call stack tuple arg_name -> position dictionary.
        id = {
                "cur_depth" : 0,
                "move"      : 1,
                "color"     : 2,
                "alpha"     : 3,
                "beta"      : 4,
                "value"     : 5,
                "alpha_orig": 6,
                "parent_ptr": 7,
                "visited"   : 8,
                "saves"     : 9
            }

        while not over:
            call_stack = [[0, [], self.color, alpha, beta, float('-inf'), alpha, 0, False, []]]
            while len(call_stack) > 0:
                # Get reference to location of current node. 
                cur_ptr = len(call_stack)-1
                # Pop node from the stack.
                [   cur_depth, 
                    move, 
                    color, 
                    alpha,
                    beta,
                    value,
                    alpha_orig, 
                    parent_ptr, 
                    visited, 
                    saves]        = call_stack.pop()
                max_depth = max(cur_depth, max_depth)
                # Negated color.
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([ 0, 
                                            [], 
                                            color, 
                                            alpha, 
                                            beta, 
                                            value, 
                                            alpha_orig, 
                                            cur_ptr, 
                                            True, 
                                            []])
                        # Generate children of root node and push onto stack. 
                        for next_move in board.get_all_moves_ref(color):
                            nodes_reached += 1
                            call_stack.append([ 1, 
                                                next_move[:], 
                                                neg_color, 
                                                -beta,
                                                -alpha, 
                                                float('-inf'),
                                                -beta,
                                                cur_ptr,
                                                False,
                                                []])
                    # Otherwise we are done with current depth-limit 
                    # iteration. Update max. 
                    else:           
                        if value > maximum:        
                            maximum = value
                            choice = move
                        over = True
                        break
                # Not at root node.
                else:
                    # If node hasn't been visited, apply move.
                    if not visited:
                        
                        for piece_move in move:
                            save = board.apply_move_retState(piece_move[0], 
                                                             piece_move[1], 
                                                             neg_color)
                            saves.append(save)

                        # Check transposition table for depth >= 2. 
                        if cur_depth >= 1:
                            key = board.get_hash_key()
                            if key in tt and tt[key]['depth'] >= max_depth - cur_depth:
                                tt_entry = tt[key]
                                v = tt_entry['value']
                                transposition_hits += 1
                                if tt_entry['flag'] == EQ:
                                    # return tt_entry value
                                    for i in range(len(saves)-1, -1, -1):
                                        board.reverse_apply_move(saves[i], neg_color)
                                    if -v > call_stack[parent_ptr][id["value"]]:
                                        call_stack[parent_ptr][id["value"]] = -v
                                        if cur_depth == 1:
                                            call_stack[parent_ptr][id["move"]] = move
                                    if -v > call_stack[parent_ptr][id["alpha"]]:
                                        call_stack[parent_ptr][id["alpha"]] = -v
                                    for i in range(parent_ptr, cur_ptr):
                                        call_stack[i][id["alpha"]] = -v
                                    continue
                                elif tt_entry['flag'] == LT:
                                    alpha = max(alpha, v)
                                elif tt_entry['flag'] == GT:
                                    beta = min(beta, v)

                                if alpha >= beta:
                                    v = tt_entry['value']
                                    # return tt_entry value
                                    for i in range(len(saves)-1, -1, -1):
                                        board.reverse_apply_move(saves[i], neg_color)
                                    if -v > call_stack[parent_ptr][id["value"]]:
                                        call_stack[parent_ptr][id["value"]] = -v
                                        if cur_depth == 1:
                                            call_stack[parent_ptr][id["move"]] = move
                                    if -v > call_stack[parent_ptr][id["alpha"]]:
                                        call_stack[parent_ptr][id["alpha"]] = -v
                                    for i in range(parent_ptr, cur_ptr):
                                        call_stack[i][id["alpha"]] = -v
                                    continue

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
                                                alpha_orig,
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
                                                alpha_orig,
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
                                                    -beta,
                                                    cur_ptr,
                                                    False,
                                                    []])
                    # Otherwise node has been visited, undo moves and propagate values up. 
                    else:

                        # Get hash key for current board.
                        hash_key = board.get_hash_key()

                        for i in range(len(saves)-1, -1, -1):
                            board.reverse_apply_move(saves[i], neg_color)
                        if -value > call_stack[parent_ptr][id["value"]]:
                            call_stack[parent_ptr][id["value"]] = -value
                            if cur_depth == 1:
                                call_stack[parent_ptr][id["move"]] = move
                        if -value > call_stack[parent_ptr][id["alpha"]]:
                            call_stack[parent_ptr][id["alpha"]] = -value
                            for i in range(parent_ptr, cur_ptr):
                                call_stack[i][id["alpha"]] = -value
                        if call_stack[parent_ptr][id["alpha"]] >= call_stack[parent_ptr][id["beta"]]:
                            nodes_pruned += (len(call_stack) - parent_ptr)
                            call_stack = call_stack[:parent_ptr+1]
                            continue
                            

                        # Transposition table caching happens here. 
                        mem = {}
                        mem['value'] = value
                        if value <= alpha_orig:
                            mem['flag'] = GT
                        elif value >= beta:
                            mem['flag'] = LT
                        else:
                            mem['flag'] = EQ
                        mem['depth'] = max_depth - cur_depth
                        tt[hash_key] = mem
        if self.verbose:
            print("MAX DEPTH", max_depth)
            print("NODES REACHED", nodes_reached)
            print("NODES EXPANDED", nodes_expanded)
            print("NODES PRUNED:", nodes_pruned)
            print("TRANSPOSITION HITS", transposition_hits)
        return (choice, maximum)


    # (IN PROGRESS)
    # negamax_pv - principal variation implementation.
    # Does not implement full negascout/principal variation search, 
    # but simply attempts to create the principal variation data structure - 
    # This is a nested dictionary structure built on each IDF iteration to save moves 
    # That cause an alpha update in the parent, which are supposedly good moves to consider 
    # first as a form of move ordering. 
    # Still very much in progress.
    def negamax_pv(self, board):
        maximum = float('-inf')
        choice = []
        over = False
        depth_limit = 1
        nodes_pruned = 0
        max_depth = 0

        cur_pv = {"best_moves": [] }
        prev_pv = {"best_moves": [] }

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
                "saves"     : 8,
                "prev_pv"   : 9,
                "cur_pv"    : 10
            }
        while not over:
            call_stack = [  [0, 
                            [], 
                            self.color, 
                            float('-inf'), 
                            float('inf'), 
                            float('-inf'), 
                            0, 
                            False, 
                            [],
                            prev_pv,
                            cur_pv
                            ]
                        ]
            while len(call_stack) > 0:
                if time.process_time() - self.start_time > self.time_limit:
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
                    saves,
                    prev_pv,
                    cur_pv]        = call_stack.pop()
                if cur_depth > max_depth:
                    max_depth = cur_depth
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([0, [], color, alpha, beta, value, cur_ptr, True, [], prev_pv, cur_pv])
                        
                        # Generate children of root node and push onto stack.    
                        for next_move in board.get_all_moves_ref(color):
                            
                            # Skip over PV moves. 
                            if tuple(next_move) in prev_pv['best_moves']:
                                continue

                            # Check if next move is a win. 
                            saves = board.apply_moves(next_move, self.color)
                            if board.game_over():
                                if self.color == "blue":
                                    if board.brown_lost():
                                        return next_move
                                else:
                                    if board.blue_lost():
                                        return next_move
                            board.reverse_apply_moves(saves, self.color)

                            next_prev_pv = {"best_moves": [] }
                            if tuple(next_move) in prev_pv:
                                next_prev_pv = prev_pv[tuple(next_move)]

                            call_stack.append([ 1, 
                                                next_move[:],
                                                neg_color, 
                                                -beta,
                                                -alpha, 
                                                float('-inf'),
                                                cur_ptr,
                                                False,
                                                [],
                                                next_prev_pv,
                                                { "best_moves"    : []}
                                            ])
                        # Next consider PV nodes.
                        if len(prev_pv['best_moves']) > 0:
                            for next_move in prev_pv['best_moves']:

                                # Check if next move is a win. 
                                saves = board.apply_moves(next_move, self.color)
                                if board.game_over():
                                    if self.color == "blue":
                                        if board.brown_lost():
                                            return next_move
                                    else:
                                        if board.blue_lost():
                                            return next_move
                                board.reverse_apply_moves(saves, self.color)

                                next_prev_pv = {"best_moves": [] }
                                if tuple(next_move) in prev_pv:
                                    next_prev_pv = prev_pv[tuple(next_move)]

                                call_stack.append([ 1, 
                                                next_move,
                                                neg_color, 
                                                -beta,
                                                -alpha, 
                                                float('-inf'),
                                                cur_ptr,
                                                False,
                                                [],
                                                next_prev_pv,
                                                { "best_moves"    : []}
                                                ])
                    # Otherwise we are done with current depth-limit 
                    # iteration. Update max. 
                    else:
                        if value > maximum:        
                            maximum = value
                            choice = move
                        prev_pv = cur_pv
                        cur_pv = { "best_moves"    : [] }
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
                                                saves,
                                                prev_pv,
                                                cur_pv
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
                                                saves,
                                                prev_pv, 
                                                cur_pv
                                              ])
                            for next_move in board.get_all_moves_ref(color):
                                # Skip over PV moves. 
                                if tuple(next_move) in prev_pv['best_moves']:
                                    continue
                                
                                next_prev_pv = {"best_moves": [] }
                                if tuple(next_move) in prev_pv:
                                    next_prev_pv = prev_pv[tuple(next_move)]

                                call_stack.append([ cur_depth+1, 
                                                    next_move[:],
                                                    neg_color, 
                                                    -beta, 
                                                    -alpha,
                                                    float('-inf'),
                                                    cur_ptr,
                                                    False,
                                                    [],
                                                    next_prev_pv,
                                                    { "best_moves"    : []}
                                                ])
                            # Next consider PV nodes.
                            if len(prev_pv['best_moves']) > 0:
                                for next_move in prev_pv['best_moves']:
                                    # Check if next move is a win. 
                                    saves = board.apply_moves(next_move, self.color)
                                    if board.game_over():
                                        if self.color == "blue":
                                            if board.brown_lost():
                                                return next_move
                                        else:
                                            if board.blue_lost():
                                                return next_move
                                    board.reverse_apply_moves(saves, self.color)

                                    next_prev_pv  = {"best_moves": [] }
                                    if tuple(next_move) in prev_pv:
                                        next_prev_pv = prev_pv[tuple(next_move)]

                                    call_stack.append([ 1, 
                                                    next_move,
                                                    neg_color, 
                                                    -beta,
                                                    -alpha, 
                                                    float('-inf'),
                                                    cur_ptr,
                                                    False,
                                                    [],
                                                    next_prev_pv,
                                                    { "best_moves"    : []}
                                                    ])
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
                            for i in range(parent_ptr, cur_ptr):
                                call_stack[i][id["alpha"]] = -value
                            # Update parent PV to include this move. 
                            call_stack[parent_ptr][id["cur_pv"]]["best_moves"].append(move)
                        if call_stack[parent_ptr][id["alpha"]] >= call_stack[parent_ptr][id["beta"]]:
                            nodes_pruned += (len(call_stack) - parent_ptr)
                            call_stack = call_stack[:parent_ptr+1]
                        
                        # Update parent PV to include child's PV. 
                        call_stack[parent_ptr][id["cur_pv"]][tuple(move)] = cur_pv
            # Increment depth limit (iterative deepening).
            depth_limit += 1
        print("NODES PRUNED:", nodes_pruned)
        print("MAX DEPTH REACHED:", max_depth)
        return choice


    # Implements Negamax (Minimax) algorithm 
    # with a very rudimentary move ordering scheme-
    # on each node expansion, first evaluate the child nodes, 
    # then sort them based off evaluation and place the best nodes at the end 
    # of the stack to be considered first. 
    def negamax_move_ordering(self, board):
        maximum = float('-inf')
        choice = []
        over = False
        start_time = time.process_time()
        depth_limit = 1
        nodes_pruned = 0
        max_depth = 0

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
                if cur_depth > max_depth:
                    max_depth = cur_depth
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([0, [], color, alpha, beta, value, cur_ptr, True, []])
                        # Generate children of root node and push onto stack. 
                        ordered = []
                        for next_move in board.get_all_moves_ref(color):
                            # Check if next move is a win. 
                            saves = board.apply_moves(next_move, color)
                            ordered.append( (next_move, self.color_weight[color] * self.evaluate_node(board)))

                            if board.game_over():
                                if self.color == "blue":
                                    if board.brown_lost():
                                        return next_move
                                else:
                                    if board.blue_lost():
                                        return next_move
                            board.reverse_apply_moves(saves,color)

                        # Order the children nodes.
                        ordered.sort(key= lambda tup:tup[1], reverse=True)
                        for next_move in ordered:
                            call_stack.append([ 1, 
                                                next_move[0][:],
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
                            depth_limit += 1
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
                            # Order the nodes.
                            ordered = []
                            for next_move in board.get_all_moves_ref(color):
                                saves = board.apply_moves(next_move, color)
                                ordered.append( (next_move, self.color_weight[color] * self.evaluate_node(board)))
                                board.reverse_apply_moves(saves, color)
                            
                            ordered.sort(key= lambda tup:tup[1])


                            for next_move in ordered:
                                call_stack.append([ cur_depth+1, 
                                                    next_move[0][:],
                                                    neg_color, 
                                                    -beta, 
                                                    -alpha,
                                                    float('-inf'),
                                                    cur_ptr,
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
                            for i in range(parent_ptr, cur_ptr):
                                call_stack[i][id["alpha"]] = -value
                        if call_stack[parent_ptr][id["alpha"]] >= call_stack[parent_ptr][id["beta"]]:
                            nodes_pruned += (len(call_stack) - parent_ptr)
                            call_stack = call_stack[:parent_ptr+1]
        print("NODES PRUNED:", nodes_pruned)
        print("MAX DEPTH REACHED:", max_depth)
        return choice

    # Apply a move, evaluate it, and return the evaluation.
    def eval_move(self, board, moves, color):
        saves = []
        for move in moves:
            save = board.apply_move_retState(move[0], move[1], color)
            saves.append(save)
        res = self.evaluate_node(board)
        board.reverse_apply_moves(saves, color)
        return self.color_weight[color] * res

    # HEURISTICS (Supplanted by the heuristics in the common Heuristics.py file)
    def enemy_royalty_count(self, counts):
        return 1-((counts["king"] + counts["prince"] + counts["duke"])/3)   

    def friendly_royalty_count(self, counts):
        return ((counts["king"] + counts["prince"] + counts["duke"])/3) 

    def enemy_pieces_remaining(self, counts):
        res = 0.0
        res += counts["knight"]
        res += counts["sergeant"]
        res += counts["pikemen"]
        res += counts["squire"]
        res += counts["archer"]
        return 1 - (res / 10.0)

    def friendly_pieces_remaining(self, counts):
        res = 0.0
        res += counts["knight"]
        res += counts["sergeant"]
        res += counts["pikemen"]
        res += counts["squire"]
        res += counts["archer"]
        return (res / 10.0)

    def in_enemy_castle(self, board, friendly_locs, enemy_castle):
        if enemy_castle[0] in friendly_locs:
            if str(friendly_locs[enemy_castle[0]]) == "archer":
                return 0.0
            return 1
        else:
            return 0.0 

    def enemy_in_castle(self, enemy_locs, friendly_castle):
        if friendly_castle[0] in enemy_locs or friendly_castle[1] in enemy_locs:
            return -1
        else:
            return 0.0 
    
    # Evaluate node using heuristic functions.
    def evaluate_node(self, board):
        if self.color == "brown":
            enemy_counts = board.blue_piece_counts
            friendly_castle = board.brown_castle
            enemy_castle = board.blue_castle
            friendly_counts = board.brown_piece_counts
            friendly_locs = board.brown_pieces_locations
            enemy_locs = board.blue_pieces_locations
            friendly_pieces = board.brown_pieces
        else:
            enemy_counts = board.brown_piece_counts
            friendly_castle = board.blue_castle
            enemy_castle = board.brown_castle
            friendly_counts = board.blue_piece_counts
            friendly_locs = board.blue_pieces_locations
            enemy_locs = board.brown_pieces_locations
            friendly_pieces = board.blue_pieces
        
        # #value = 0.0
        # v1 = self.enemy_royalty_count(enemy_counts)
        # v2 = self.enemy_pieces_remaining(enemy_counts)
        v6 = self.in_enemy_castle(board, friendly_locs, enemy_castle)
        # #v4 = self.enemy_in_castle(enemy_locs, friendly_castle)
        # v5 = self.friendly_pieces_remaining(friendly_counts)
        # v6 = self.friendly_royalty_count(friendly_counts)
        #v7 = self.friendly_royalty_avengeable(board, friendly_pieces, friendly_locs, friendly_counts)
        #v8 = self.proximity_pieces(friendly_locs, friendly_castle)
        # #v9 = distance_to_enemy_castle(board, self.color)
        # return v1 + v2 + v5 + v6 + v3
        
        v1 = royalty_remaining(board, self.color)
        v2 = 1 - royalty_remaining(board, self.neg_color)
        v3 = other_remaining(board, self.color)
        v4 = 1 - other_remaining(board, self.neg_color)
        v5 = distance_to_enemy_castle(board, self.color)
        return .2*v1 + .2*v2 + .2*v3 + .2*v4 + .1*v5 + .1*v6

    def friendly_royalty_avengeable(self, board, pieces, friendly_locs, friendly_counts):
        royalty_locs_covered = set()
        upper_bound = friendly_counts["king"] + friendly_counts["prince"] + friendly_counts["duke"]

        # Iterate over all piece moves and if a royalty position is covered,
        # add it to the covered set
        for piece in pieces:
            for (x,y) in piece.get_moves_w_avg(board, friendly_locs, dict()):
                if (x,y) in friendly_locs:
                    if str(friendly_locs[(x,y)]) in ["king", "prince", "duke"]: 
                        royalty_locs_covered.add((x,y))
                if len(royalty_locs_covered) == upper_bound:
                    break
        return (len(royalty_locs_covered) / 3)

    def proximity_pieces(self, friendly_locations, friendly_castle):
       
        maximum = 118.99019513592785

        # Euclidean Distance
        def d(p1,p2):
            return math.sqrt(math.pow((p1[0]-p2[0]),2) + 
                             math.pow((p1[1]-p2[1]),2))
    
        pts = []
        for loc,piece in friendly_locations.items():
            if str(piece) in ["king", "squire", "archer"]:
                pts.append(loc)
        pts.append(friendly_castle[0])
        res = 0.0
        for i in range(len(pts)-1):
            for j in range((i+1),len(pts)):
                res += d(pts[i],pts[j])
        return 1 - (res/maximum)
    
