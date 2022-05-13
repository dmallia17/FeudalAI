from Board import *
from LocalSearch import *
import time

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain_3M_official_1.txt")

    prev_time = time.process_time()
    blue_local_search = SimulatedAnnealing(b, "blue")
    new_config = blue_local_search.get_piece_placement(10,.99)
    print(time.process_time() - prev_time)

    b.place_pieces("blue", new_config)
    b.display()
