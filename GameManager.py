from Board import *
import argparse, random
# "Agent Classes"
# NEED:
# - Human
# - Random
# - Minimax
# - MCTS
# - RL?

# IMPLIES:
# - FINISH SQUIRE, FINISH ARCHER MOVE CHECKING (i.e. if hit a castle green and
# another move is possible beyond the green AND there is an enemy beyond, then
# yield the move)
# - AGENT FUNCTIONS: get_piece_placement, get_choice
# - BOARD FUNCTIONS: get_all_moves, apply_move, remove_piece
# Put a check that the castle hasn't been separated?


agent_dict = {
    "human" : Human
}

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the Feudal board game")
    parser.add_argument("terrain_file", type=str, metavar="filename",
        help=".txt file containing the board layout")
    # UPDATE THESE AS MORE BECOME AVAILABLE
    parser.add_argument("agent1_type", type=str, choices=["human"],
        help="Selection for first player, options are: human")
    parser.add_argument("agent2_type", type=str, choices=["human"],
        help="Selection for second player, options are: human")
    args = parser.parse_args()

    # Create Board
    game_board = Board()
    game_board.parse_terrain(args.terrain_file)

    # Set up agents
    brown_player = agent_dict[args.agent1_type]()
    blue_player = agent_dict[args.agent2_type]()

    # Setup pieces
    config = brown_player.get_piece_placement(game_board.clone())
    game_board.place_pieces("brown", config)
    config = blue_player.get_piece_placement(game_board.clone())
    game_board.place_pieces("blue", config)

    # Flip a coin for which player goes first
    blue_turn = bool(random.getrandbits(1))

    # While not game over, run game
    while not game_board.gameover():
        # Show the state of the game - NOTE: comment out if not needed
        game_board.display()

        if blue_turn:
            print("BLUE PLAYER:")
            move = blue_player.get_choice(game_board.clone())
            if not game_board.apply_move(move):
                print("Invalid move")

        else: # Brown turn
            print("BROWN PLAYER")
            move = brown_player.get_choice(game_board.clone())
            if not game_board.apply_move(move):
                print("Invalid move")

        # For the future - save out game state if relevant

        blue_turn = not blue_turn

    if game_board.blue_lost():
        print("BROWN WON")
    else:
        print("BLUE WON")


