# Module for method to optimize the local search done for piece setup

from itertools import combinations
import math, multiprocessing, random, time
from Board import *
from FeudalUtilities import parallel_seed
from GameExecution import run_game_simulation_truncated
from Heuristics import simple_piece_evaluation
from LocalSearch import HillClimbingFirstChoice
from MCTS import PieceGreedyRandomPlayoutAgent


def prep_and_run_local_search(board, agent_type, blue_weights, brown_weights,
    agent_run_args=dict()):
    new_board = board.clone()

    # Get agents
    blue_agent = agent_type(board.clone(), "blue", *blue_weights)
    brown_agent = agent_type(board.clone(), "brown", *brown_weights)

    # Get configs
    blue_config = blue_agent.get_piece_placement(**agent_run_args)
    brown_config = brown_agent.get_piece_placement(**agent_run_args)

    # Place on a new board - done so that the map operation can be run for
    # simplicity
    new_board.place_pieces("blue", blue_config)
    new_board.place_pieces("brown", brown_config)
    return new_board

class LocalSearchOptimizer():
    # @param step_size          The size of the "step" to take in incrementing/
    #                           decrementing weight values - NOTE: 1 divided by
    #                           this value MUST BE an integer.
    # @param num_weights        How many weights are being optimized
    # @param num_setups         The number of setups to try for each given
    #                           set of weights.
    # @param num_simulations    How many game simulations to conduct in
    #                           evaluating each particular setup for a given
    #                           set of weights.
    # @param terrain_file       The terrain with which to instantiate the board
    #                           used for all simulations.
    def __init__(self, step_size=.1, num_weights=7, num_setups=8,
        num_simulations=8, turn_limit=3, eval_func=simple_piece_evaluation,
        play_agent = PieceGreedyRandomPlayoutAgent, play_agent_args=dict(),
        terrain_file="terrain_3M_official_1.txt",
        num_processes=8, search_agent=HillClimbingFirstChoice,
        agent_run_args=dict()):
        self.step_size = step_size
        self.num_weights = num_weights
        self.num_setups = num_setups
        self.num_simulations = num_simulations
        self.turn_limit = turn_limit
        self.eval_func = eval_func
        self.combinations = [list(x) for x in list(
            combinations(list(range(self.num_weights)), 2))]
        self.board = Board()
        self.board.parse_terrain(terrain_file)
        self.playout_blue = play_agent("blue", **play_agent_args)
        self.playout_brown = play_agent("brown", **play_agent_args)
        self.uniform_weights = [1.0 / num_weights] * num_weights
        self.sim_pool = multiprocessing.Pool(processes=num_processes,
            initializer=parallel_seed)
        self.search_agent = search_agent
        self.agent_run_args = agent_run_args

    # NOTE: ANY USAGE OF THIS AGENT MUST CALL THIS FUNCTION AT CONCLUSION
    # Properly closes the pool of processes used for simulation
    def cleanup(self):
        self.sim_pool.close()
        self.sim_pool.join()

    # Get a random set of weights
    def get_random_start(self):
        weights = [0] * self.num_weights
        for _ in range(int(1/(self.step_size))):
            choice = random.randrange(self.num_weights)
            weights[choice] += self.step_size
        return weights

    def get_random_successor(self, weights):
        # Get a pair of weights
        swap_indices = random.choice(self.combinations)
        # Cannot choose two zero weights
        while (weights[swap_indices[0]] - 0 < 0.00001 and \
            weights[swap_indices[1]] - 0 < 0.00001):
            swap_indices = random.choice(self.combinations)

        # Shuffle the indices (note: this shuffles in place, modifying the
        # pair of indices in self.combinations - however this likely doesn't
        # add any more bias to which is incremented or decremented than
        # reshuffling from an original ordering each time)
        random.shuffle(swap_indices)
        # If the index to be decremented is the zero weight, swap
        if weights[swap_indices[1]] - 0 < 0.00001:
            swap_indices[0], swap_indices[1] = swap_indices[1], swap_indices[0]
        new_weights = weights[:]
        # Increment the first term, decrement the second, by step_size
        new_weights[swap_indices[0]] += self.step_size
        new_weights[swap_indices[1]] -= self.step_size
        return new_weights

    # Return the win ratio for the blue player using the new weights, whereas
    # the brown player is still using UNIFORM weights
    def evaluate(self, weights):
        # For the number of setups requested, prepare boards for gameplay
        args = [(self.board, self.search_agent, weights, self.uniform_weights,
            self.agent_run_args) for _ in range(self.num_setups)]
        game_starts = self.sim_pool.starmap(prep_and_run_local_search, args)
        print("Completed game starts")

        # For the number of simulations requested, run games from each start
        # Flip a coin for which player goes first
        results = []
        for curr_start in game_starts:
            curr_results = self.sim_pool.starmap(run_game_simulation_truncated,
                [(self.turn_limit, self.eval_func, curr_start.clone(),
                self.playout_blue, self.playout_brown,
                bool(random.getrandbits(1)), time.time(), math.inf) \
                    for _ in range(self.num_simulations)])
            results += [x[0] for x in curr_results]

        # Return the win ratio for blue
        return len([r for r in results if r == "blue"]) / len(results)

    # @param t is initial temperature.
    # @param c is a constant 0 < c < 1 which controls cooling.
    def get_weights(self,  t_init=1, alpha=.01):
        print("OPTIMIZING...")
        current = self.get_random_start()
        print("Initial weights:", current)

        time = 1
        while True:
            # exponential temperature decrease.
            t_curr = t_init * (math.pow(alpha,time))
            # effective "zero" temp.
            if t_curr < .000001:
                break
            succ = self.get_random_successor(current)

            # Calculate value difference between current and random config.
            delta = self.evaluate(current) - self.evaluate(succ)

            # If delta < 0, value of the random config is greater, i.e. 
            # we found a better state. So go there.
            if delta < 0:
                current = succ
            # If delta > 0, we pick the worse state with a probability 
            # in accord to the Boltzmann distribution.
            else:
                rand = random.uniform(0,1)
                if rand < (math.exp(((-delta)/t_curr))):
                    current = succ
            time += 1

        print("Final weights:", current)
        return current


