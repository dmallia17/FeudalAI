from Board import *
from LocalSearch import *

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain.txt")
    # Setup blue
    blue_local_search = LocalSearch(b, "blue")
    blue_config = blue_local_search.get_random_start()
    # print(blue_config)
    print(b.place_pieces("blue", blue_config))
    # Setup brown
    print(b.place_pieces("brown", LocalSearch(b, "brown").get_random_start()))
    # print(b.blue_pieces)
    # print(b.blue_pieces_locations)
    # print(b.blue_piece_counts)
    print(len(blue_local_search.get_successor_states(blue_config)))
    successor = blue_local_search.get_random_successor(blue_config)
    for k,v in blue_config.items():
        if successor[k] != blue_config[k]:
            print(k, v)
            print(k, successor[k])
    #print(blue_local_search.evaluate_config(blue_config))
    #b.display()

    b2 = Board()
    b2.parse_terrain("terrain.txt")
    searcher = HillClimbingFirstChoice(b2, "blue")
    new_config = searcher.get_piece_placement()
    print(b2.place_pieces("blue", new_config))
    print(new_config)
    b2.display()
    # print(searcher.royalty_avengeable(new_config))
    # print(searcher.non_royalty_avengeable(new_config))
