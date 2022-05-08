from Board import *
from LocalSearch import *
from time import perf_counter
import sys
import random

if __name__ == "__main__":
    random.seed(1)
    b3 = Board()
    b3.parse_terrain("terrain_3M_official_1.txt")
    blue_searcher = HillClimbingFirstChoice(b3, "blue")
    brown_searcher = HillClimbingFirstChoice(b3, "brown")
    blue_random = blue_searcher.get_random_start()
    brown_random = brown_searcher.get_random_start()
    b3.place_pieces("blue", blue_random)
    b3.place_pieces("brown", brown_random)

    save = b3.apply_move_retState((12,4),(5,11),"brown")
    b3.reverse_apply_move(save, "brown")
    b3.display()


