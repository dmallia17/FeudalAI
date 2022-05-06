from Board import *
from LocalSearch import *
from time import perf_counter

if __name__ == "__main__":
    b3 = Board()
    b3.parse_terrain("terrain_3M_official_1.txt")
    blue_searcher = HillClimbingFirstChoice(b3, "blue")
    brown_searcher = HillClimbingFirstChoice(b3, "brown")
    blue_random = blue_searcher.get_random_start()
    brown_random = brown_searcher.get_random_start()
    b3.place_pieces("blue", blue_random)
    b3.place_pieces("brown", brown_random)
    b3.display()
    

    start = perf_counter()
    move_counter = 0
    for move in b3.get_all_moves("brown"):
        move_counter += 1
    print("moves generated (get_all_moves): ", move_counter)
    end = perf_counter()
    print("Time elapsed: ", (end-start), "\n")


    start = perf_counter()
    num_moves = b3.get_num_all_moves("brown")
    print("moves generated (get_num_moves): ", move_counter)
    end = perf_counter()
    print("Time elapsed: ", (end-start))
