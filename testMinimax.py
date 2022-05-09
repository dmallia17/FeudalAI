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
    count = 0
    for m in b3.get_all_moves_ref("brown"):
        count += 1
    end = perf_counter()
    print("Time elapsed (get_all_moves_ref): ", (end-start))
    print("num moves generated: ", count)
    print()

    start = perf_counter()
    count = 0
    for m in b3.get_all_moves("brown"):
        count += 1
    end = perf_counter()
    print("Time elapsed (get_all_moves): ", (end-start))
    print("num moves generated: ", count)
    print()

    start = perf_counter()
    test = b3.get_num_all_moves("brown")
    end = perf_counter()
    print("Time elapsed (get_num_all_moves): ", (end-start))
    print(test)
