from Board import *
from LocalSearch import *
from time import perf_counter

if __name__ == "__main__":
    # b = Board()
    # b.parse_terrain("terrain_3M_official_1.txt")
    # Setup blue
    # blue_local_search = LocalSearch(b, "blue")
    # blue_config = blue_local_search.get_random_start()
    # print(blue_config)
    # print(b.place_pieces("blue", blue_config))
    # Setup brown
    # print(b.place_pieces("brown", LocalSearch(b, "brown").get_random_start()))
    # print(b.blue_pieces)
    # print(b.blue_pieces_locations)
    # print(b.blue_piece_counts)
    # print(len(blue_local_search.get_successor_states(blue_config)))
    # successor = blue_local_search.get_random_successor(blue_config)
    # for k,v in blue_config.items():
    #     if successor[k] != blue_config[k]:
    #         print(k, v)
    #         print(k, successor[k])
    #print(blue_local_search.evaluate_config(blue_config))
    #b.display()

    # b2 = Board()
    # b2.parse_terrain("terrain_3M_official_1.txt")
    # blue_searcher = HillClimbingFirstChoice(b2, "blue")
    # new_blue_config = blue_searcher.get_piece_placement()
    # print(b2.place_pieces("blue", new_config))
    # print(new_config)
    # brown_searcher = HillClimbingFirstChoice(b2, "brown")
    # new_brown_config = brown_searcher.get_piece_placement()
    # b2.place_pieces("blue", new_blue_config)
    # b2.place_pieces("brown", new_brown_config)
    # b2.display()

    b3 = Board()
    b3.parse_terrain("terrain_3M_official_1.txt")
    blue_searcher = HillClimbingFirstChoice(b3, "blue")
    brown_searcher = HillClimbingFirstChoice(b3, "brown")
    blue_random = blue_searcher.get_random_start()
    brown_random = brown_searcher.get_random_start()
    b3.place_pieces("blue", blue_random)
    b3.place_pieces("brown", brown_random)
    start = perf_counter()
    test = b3.get_random_move("blue")[0]
    end = perf_counter()
    print("Time elapsed: ", (end-start))
    print(test)
    # print(searcher.royalty_avengeable(new_config))
    # print(searcher.non_royalty_avengeable(new_config))
