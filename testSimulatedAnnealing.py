from Board import *
from LocalSearch import *

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain.txt")

    blue_local_search = SimulatedAnnealing(b, "blue")
    blue_config = blue_local_search.get_random_start()

    new_config = blue_local_search.get_piece_placement(blue_config,10,.99)

    b.place_pieces("blue", new_config)
    b.display()
