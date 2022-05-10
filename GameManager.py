from Board import *
from Agent import RandomAgent, PureGreedyRandomAgent
from MCTS import MCTS_UCT_Agent, MCTS_UCT_LP_Agent
from Minimax import Minimax_Agent
from GameExecution import *
import argparse, json, random
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
    # "human"     : Human,
    "random"    : RandomAgent,
    "mcts_uct"  : MCTS_UCT_Agent,
    "minimax"   : Minimax_Agent,
    "mcts_uct_lp" : MCTS_UCT_LP_Agent,
    "puregreedyrandom" : PureGreedyRandomAgent
}

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the Feudal board game")
    parser.add_argument("json_input", type=str, metavar="filename",
        help=".json file specifying game run parameters")
    args = parser.parse_args()

    with open(args.json_input, "r") as f:
        game_params = json.load(f)

    # Possibly seed
    if game_params["seed"] is not None:
        random.seed(game_params["seed"])

    # Create Board
    game_board = Board(game_params["num_moves_permitted"])
    game_board.parse_terrain(game_params["terrain"])

    # Set up agents
    # 1. Fetch params
    blue_spec = game_params["blue"]
    brown_spec = game_params["brown"]

    # 2. insert colors (avoiding spec errors in json), as well as args for the
    # LocalSearch method
    blue_spec["args"]["color"] = "blue"
    blue_spec["args"]["local_search_init_args"]["board"] = game_board.clone()
    blue_spec["args"]["local_search_init_args"]["color"] = "blue"
    brown_spec["args"]["color"] = "brown"
    brown_spec["args"]["local_search_init_args"]["board"] = game_board.clone()
    brown_spec["args"]["local_search_init_args"]["color"] = "brown"

    # 3. Instantiate agents
    blue_player = agent_dict[blue_spec["type"]](**blue_spec["args"])
    brown_player = agent_dict[brown_spec["type"]](**brown_spec["args"])


    # Setup pieces
    # NORMAL SETUP
    setup_choice = game_params["setup"]
    if "local" == setup_choice:
        config = blue_player.get_piece_placement(game_board.clone())
        game_board.place_pieces("blue", config)
        config = brown_player.get_piece_placement(game_board.clone())
        game_board.place_pieces("brown", config)
    # FAST SETUP
    elif "random" == setup_choice:
        config = blue_player.local_search_method.get_random_start()
        game_board.place_pieces("blue", config)
        config = brown_player.local_search_method.get_random_start()
        game_board.place_pieces("brown", config)
    else:
        raise RuntimeError("Invalid setup type given")

    # Flip a coin for which player goes first
    blue_turn = bool(random.getrandbits(1))

    # Run the game
    run_game_verbose(game_board, blue_player, brown_player, blue_turn)

    # Handle any cleanup for multiprocessing
    if type(blue_player) == MCTS_UCT_LP_Agent:
        blue_player.cleanup()
        print("blue cleaned")

    if type(brown_player) == MCTS_UCT_LP_Agent:
        brown_player.cleanup()
        print("brown cleaned")


