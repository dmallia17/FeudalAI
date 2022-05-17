# Script to run many trials of a configuration and report statistics

import argparse, json, datetime, os, pickle, random
from Board import *
from Agent import RandomAgent, PureGreedyRandomAgent, PieceGreedyRandomAgent
from MCTS import MCTS_UCT_Agent, MCTS_UCT_LP_Agent
from Minimax import Minimax_Agent
from GameExecution import *
from GameManager import *


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Run the Feudal board game and report stats")
    parser.add_argument("json_input", type=str, metavar="filename",
        help=".json file specifying game run parameters")
    parser.add_argument("--num_trials", type=int, default=10,
        metavar="integer",
        help="How many times to run a game for the given configuration")
    parser.add_argument("--no_record", action="store_false",
        help="Pass to skip on recording of the game")
    args = parser.parse_args()

    recording = args.no_record
    config_name = os.path.splitext(os.path.basename(args.json_input))[0]

    # Initial setup
    with open(args.json_input, "r") as f:
        game_params = json.load(f)

    # Possibly seed
    if game_params["seed"] is not None:
        random.seed(game_params["seed"])

    ### STAT COLLECTION
    winners, turn_counts = [], []
    # Lists of dictionaries, each representing whatever statistics are returned
    # by each agent type
    blue_stats_all, brown_stats_all = [], []

    setup_choice = game_params["setup"]
    # Set up static parameters for agents
    blue_spec = game_params["blue"]
    brown_spec = game_params["brown"]
    blue_spec["args"]["color"] = "blue"
    blue_spec["args"]["local_search_init_args"]["color"] = "blue"
    brown_spec["args"]["color"] = "brown"
    brown_spec["args"]["local_search_init_args"]["color"] = "brown"


    for i in range(args.num_trials):
        # Create Board
        game_board = Board(game_params["num_moves_permitted"])
        game_board.parse_terrain(game_params["terrain"])

        # Add board args for the LocalSearch methods
        blue_spec["args"]["local_search_init_args"]["board"] = \
            game_board.clone()
        brown_spec["args"]["local_search_init_args"]["board"] = \
            game_board.clone()

        # Instantiate agents
        blue_player = agent_dict[blue_spec["type"]](**blue_spec["args"])
        brown_player = agent_dict[brown_spec["type"]](**brown_spec["args"])

        # Setup pieces
        # NORMAL SETUP
        if "local" == setup_choice:
            blue_config = blue_player.get_piece_placement(game_board.clone())
            brown_config = brown_player.get_piece_placement(game_board.clone())
            game_board.place_pieces("blue", blue_config)
            game_board.place_pieces("brown", brown_config)
        # FAST SETUP
        elif "random" == setup_choice:
            blue_config = blue_player.local_search_method.get_random_start()
            brown_config = brown_player.local_search_method.get_random_start()
            game_board.place_pieces("blue", blue_config)
            game_board.place_pieces("brown", brown_config)
        else:
            raise RuntimeError("Invalid setup type given")

        # Flip a coin for which player goes first
        blue_turn = bool(random.getrandbits(1))

        # Run the game
        winner, turn_count, game_states, blue_stats, brown_stats = \
            run_game_trial(game_board, blue_player, brown_player, blue_turn)
        winners.append(winner)
        turn_counts.append(turn_count)
        blue_stats_all.append(blue_stats)
        brown_stats_all.append(brown_stats)

        # Handle any cleanup for multiprocessing
        if type(blue_player) == MCTS_UCT_LP_Agent:
            blue_player.cleanup()
            print("blue cleaned")

        if type(brown_player) == MCTS_UCT_LP_Agent:
            brown_player.cleanup()
            print("brown cleaned")

        # Write out the game
        if recording:
            fname = config_name + "_trial_" + str(i) + "_" + \
                    datetime.datetime.now().strftime("%m_%d-%H_%M_%S") + ".pkl"
            with open(fname, "wb") as f:
                pickle.dump(game_states, f)

    # Prepare stats report
    blue_agent_name = blue_spec["type"].upper()
    brown_agent_name = brown_spec["type"].upper()

    blue_wins_count = len([w for w in winners if w == "blue"])
    brown_wins_count = args.num_trials - blue_wins_count

    total_turns = sum(turn_counts)
    avg_num_turns = total_turns / args.num_trials
    max_num_turns = max(turn_counts)
    min_num_turns = min(turn_counts)

    blue_final_report = {}
    for stat in blue_stats_all[0].keys():
        blue_final_report[stat] = {}
        all_stat = []
        for game in blue_stats_all:
            all_stat += game[stat]
        blue_final_report[stat]["MIN"] = min(all_stat)
        blue_final_report[stat]["MAX"] = max(all_stat)
        blue_final_report[stat]["AVG"] = sum(all_stat) / len(all_stat)

    brown_final_report = {}
    for stat in brown_stats_all[0].keys():
        brown_final_report[stat] = {}
        all_stat = []
        for game in brown_stats_all:
            all_stat += game[stat]
        brown_final_report[stat]["MIN"] = min(all_stat)
        brown_final_report[stat]["MAX"] = max(all_stat)
        brown_final_report[stat]["AVG"] = sum(all_stat) / len(all_stat)

    timepoint = datetime.datetime.now().strftime("%m_%d-%H_%M_%S")
    fname = config_name + "_REPORT_" + timepoint + ".txt"
    with open(fname, "w") as f:
        f.write(config_name + " Report " + timepoint + "\n")
        f.write("Number of trials conducted: " + str(args.num_trials) + "\n")
        f.write(blue_agent_name + " won " + str(blue_wins_count) + " out of " \
            + str(args.num_trials) + " games\n")
        f.write(brown_agent_name + " won " + str(brown_wins_count) + \
            " out of " + str(args.num_trials) + " games\n")
        f.write("Minimum game length was " + str(min_num_turns) + " turns\n")
        f.write("Maximum game length was " + str(max_num_turns) + " turns\n")
        f.write("Average game length was " + str(avg_num_turns) + " turns\n")
        f.write("\n\nBLUE STATS REPORT:\n")
        for stat in blue_final_report.keys():
            f.write(stat + ":\n")
            for suff_stat in blue_final_report[stat].keys():
                f.write(suff_stat + " " + \
                    str(blue_final_report[stat][suff_stat]) + "\n")
            f.write("\n")

        f.write("\nBROWN STATS REPORT:\n")
        for stat in brown_final_report.keys():
            f.write(stat + ":\n")
            for suff_stat in brown_final_report[stat].keys():
                f.write(suff_stat + " " + \
                    str(brown_final_report[stat][suff_stat]) + "\n")
            f.write("\n")

