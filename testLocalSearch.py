from Board import *
from LocalSearch import *

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain.txt")
    # Setup blue
    blue_local_search = LocalSearch(b, (0,11))
    blue_config = blue_local_search.get_random_start()
    # print(blue_config)
    print(b.place_pieces("blue", blue_config))
    # Setup brown
    print(b.place_pieces("brown", LocalSearch(b, (12,23)).get_random_start()))
    # print(b.blue_pieces)
    # print(b.blue_pieces_locations)
    # print(b.blue_piece_counts)
    print(len(blue_local_search.get_successor_states(blue_config)))
    successor = blue_local_search.get_random_successor(blue_config)
    for k,v in blue_config.items():
        if successor[k] != blue_config[k]:
            print(k, v)
            print(k, successor[k])
    b.display()
