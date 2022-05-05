# Functions for running the game

# Basic execution of the game in verbose fashion - showing whose turn it is and
# displaying the board
def run_game_verbose(game_board, blue_player, brown_player, blue_turn):
    while not game_board.game_over():
        game_board.display()

        if blue_turn:
            print("BLUE PLAYER:")
            move = blue_player.get_choice(game_board.clone())
            for m in move:
                if not game_board.apply_move(m[0], m[1], "blue"):
                    print("Invalid move")
        else: # Brown turn
            print("BROWN PLAYER")
            move = brown_player.get_choice(game_board.clone())
            for m in move:
                if not game_board.apply_move(m[0], m[1], "brown"):
                    print("Invalid move")

        blue_turn = not blue_turn

    if game_board.blue_lost():
        print("BROWN WON")
        game_board.display()
    else:
        print("BLUE WON")
        game_board.display()
