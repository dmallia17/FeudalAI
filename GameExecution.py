# Functions for running the game

from time import time

# @param    d   a dictionary in the counts format from Board
def print_piece_counts(d):
    royalty_line = "ROYALTY King    %d Prince    %d Duke    %d"
    other_line =   "OTHER   Knights %d Sergeants %d Pikemen %d " + \
        "Squire %d Archer %d"
    print(royalty_line % (d["king"], d["prince"], d["duke"]))
    print(other_line % (d["knight"], d["sergeant"], d["pikemen"], d["squire"],
        d["archer"]))

# Basic execution of the game in verbose fashion - showing whose turn it is and
# displaying the board
def run_game_verbose(game_board, blue_player, brown_player, blue_turn):
    num_turns = 0
    while not game_board.game_over():
        game_board.display()

        if blue_turn:
            print("BLUE PLAYER:")
            # The time function may not be the most accurate for this, but it
            # skirts any issues with multiprocessing
            start = time()
            move = blue_player.get_choice(game_board.clone())
            end = time()
            print("Time elapsed:", end-start)
            for m in move:
                if not game_board.apply_move(m[0], m[1], "blue"):
                    print("Invalid move")
        else: # Brown turn
            print("BROWN PLAYER")
            start = time()
            move = brown_player.get_choice(game_board.clone())
            end = time()
            print("Time elapsed:", end-start)
            for m in move:
                if not game_board.apply_move(m[0], m[1], "brown"):
                    print("Invalid move")

        blue_turn = not blue_turn
        num_turns += 1

    if game_board.blue_lost():
        print("BROWN WON")
        game_board.display()
    else:
        print("BLUE WON")
        game_board.display()
    print("NUMBER OF TURNS:", num_turns)
    print("BLUE PIECE COUNTS:")
    print_piece_counts(game_board.blue_piece_counts)
    print("BROWN PIECE COUNTS:")
    print_piece_counts(game_board.brown_piece_counts)



# Silent execution of game; returns the winner of the game as a string
# @return   Returns the color (string) of the winner and the number of turns
#           in the simulation
def run_game_simulation(game_board, blue_player, brown_player, blue_turn,
    start_time, limit):
    num_turns = 0
    while not game_board.game_over():
        if (time() - start_time > limit):
            return None

        if blue_turn:
            move = blue_player.get_choice(game_board.clone())
            for m in move:
                if not game_board.apply_move(m[0], m[1], "blue"):
                    print("Invalid move")
        else: # Brown turn
            move = brown_player.get_choice(game_board.clone())
            for m in move:
                if not game_board.apply_move(m[0], m[1], "brown"):
                    print("Invalid move")

        blue_turn = not blue_turn
        num_turns += 1

    if game_board.blue_lost():
        return "brown", num_turns
    else:
        return "blue", num_turns

# Very similar to run_game_simulation except with checking for early
# termination and use of an evaluation function if truncated.
# @param limit          the TIME limit on the game
# @param turn_limit     the number of turns permitted before the simulation
#                       should be truncated, with the winner reported via
#                       evaluation function
def run_game_simulation_truncated(turn_limit, eval_func, game_board,
    blue_player, brown_player, blue_turn, start_time, limit):
    num_turns = 0
    turn_limit_reached = False
    while not game_board.game_over() and not turn_limit_reached:
        if (time() - start_time > limit):
            return None

        if blue_turn:
            move = blue_player.get_choice(game_board.clone())
            for m in move:
                if not game_board.apply_move(m[0], m[1], "blue"):
                    print("Invalid move")
        else: # Brown turn
            move = brown_player.get_choice(game_board.clone())
            for m in move:
                if not game_board.apply_move(m[0], m[1], "brown"):
                    print("Invalid move")

        blue_turn = not blue_turn
        num_turns += 1
        if num_turns == turn_limit:
            turn_limit_reached = True

    if turn_limit_reached: # If game was truncated
        return eval_func(game_board), num_turns
    else: # If the game otherwise concluded
        if game_board.blue_lost():
            return "brown", num_turns
        else:
            return "blue", num_turns
