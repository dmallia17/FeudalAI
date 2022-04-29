from Board import *
from LocalSearch import *

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain.txt")
    # Setup blue
    blue_config = LocalSearch().get_random_start(b, (0,11))
    print(blue_config)
    print(b.place_pieces("blue", blue_config))
    # Setup brown
    print(b.place_pieces("brown", LocalSearch().get_random_start(b, (12,23))))
    print(b.blue_pieces)
    print(b.blue_pieces_locations)
    print(b.blue_piece_counts)
    b.display()
