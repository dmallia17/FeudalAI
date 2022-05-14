import random
from Board import *
from Agent import *
import time

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
        self.start_time = None

    def get_choice(self, board):
        self.start_time = time.process_time()
        self.tt = {}
        return self.negamax(board)
        #return self.iter_deepening(board)


    # Iterative deepening for MTD(f). 
    def iter_deepening(self, board):
        value_guess = 0
        for depth in range(1,5):
            (choice, value_guess) = self.MTD_F(board, value_guess, depth)
            print(depth)
            if time.process_time() - self.start_time > self.time_limit:
                break
        return choice

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

    # Implements Negamax (Minimax) algorithm with transposition tables for MTD_F.
    def negamax_with_mem_MTD_F(self, board, alpha, beta, max_depth):
        
        maximum = float('-inf')
        choice = []
        over = False
        nodes_pruned = 0
        transposition_hits = 0
        useful_transposition_hits = 0
        
        # Transposition Table
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
                            if key in tt and tt[key]['depth'] >= cur_depth:
                                tt_entry = tt[key]
                                v = tt_entry['value']
                                if cur_depth < max_depth:
                                    useful_transposition_hits += 1
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
                        if board.game_over() or cur_depth == max_depth:
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
                        mem['depth'] = cur_depth
                        tt[hash_key] = mem

        print("NODES PRUNED:", nodes_pruned)
        print("TRANSPOSITION HITS", transposition_hits)
        print("USEFUL TRANSPO HITS", useful_transposition_hits)
        return (choice, maximum)


    # Implements Negamax (Minimax) algorithm with transposition tables (Not for MTD_F).
    def negamax_with_mem(self, board):
        
        maximum = float('-inf')
        choice = []
        over = False
        nodes_pruned = 0
        transposition_hits = 0
        useful_transposition_hits = 0
        depth_limit = 1
        
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
                            if key in tt and tt[key]['depth'] >= cur_depth:
                                tt_entry = tt[key]
                                v = tt_entry['value']
                                if cur_depth < depth_limit:
                                    useful_transposition_hits += 1
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
                        mem['depth'] = cur_depth
                        tt[hash_key] = mem
            depth_limit += 1
        print("NODES PRUNED:", nodes_pruned)
        print("TRANSPOSITION HITS", transposition_hits)
        print("USEFUL TRANSPO HITS", useful_transposition_hits)
        return choice
















    # Implements Negamax (Minimax) algorithm.
    def negamax(self, board):
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
                #print(call_stack)
                # Pop node from the stack.
                #print(call_stack)
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
                print(value)
                neg_color = "brown" if color == "blue" else "blue"
                # If at root node.
                if cur_depth == 0:
                    # Check visited as flag to determine if moves need to be 
                    # generated (Since root move is initially None). 
                    if False == visited:
                        # First push the root back onto the stack. 
                        call_stack.append([0, [], color, alpha, beta, value, cur_ptr, True, []])
                        # Generate children of root node and push onto stack. 
                        
                        cluster = {}
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
                            board.reverse_apply_moves(saves, self.color)


                            eval = self.eval_move(board, next_move, self.color)
                            if eval in cluster:
                                cluster[eval].append(next_move)
                            else:
                                cluster[eval] = [next_move]

                        for eval,moves in cluster.items():

                            call_stack.append([ 1, 
                                                random.choice(moves)[:], 
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
                            cluster = {}
                            for next_move in board.get_all_moves_ref(color):
                                eval = self.eval_move(board, next_move, color)
                                if eval in cluster:
                                    cluster[eval].append(next_move)
                                else:
                                    cluster[eval] = [next_move]
                            for _,moves in cluster.items():
                                call_stack.append([ cur_depth+1, 
                                                    random.choice(moves)[:], 
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

















    def eval_move(self, board, moves, color):
        saves = []
        for move in moves:
            save = board.apply_move_retState(move[0], move[1], color)
            saves.append(save)
        res = self.evaluate_node(board)
        board.reverse_apply_moves(saves, color)
        return self.color_weight[color] * res

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

    def in_enemy_castle(self, friendly_locs, enemy_castle):
        if enemy_castle[0] in friendly_locs or enemy_castle[1] in friendly_locs:
            return 10.0
        else:
            return 0.0 

    def enemy_in_castle(self, enemy_locs, friendly_castle):
        if friendly_castle[0] in enemy_locs or friendly_castle[1] in enemy_locs:
            return -10.0
        else:
            return 0.0 
    
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
        
        value = 0.0
        value += self.enemy_royalty_count(enemy_counts)
        value += self.enemy_pieces_remaining(enemy_counts)
        value += self.in_enemy_castle(friendly_locs, enemy_castle)
        value += self.enemy_in_castle(enemy_locs, friendly_castle)
        value += self.friendly_pieces_remaining(friendly_counts)
        value += self.friendly_royalty_count(friendly_counts)
        value += self.friendly_royalty_avengeable(board, friendly_pieces, friendly_locs, friendly_counts)
        value += self.proximity_pieces(friendly_locs, friendly_castle)
        return value
        
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
    
