from Board import *
from Minimax import *


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

    
    agent = Minimax_Agent("brown", 5.0, None,None,None)

    print(agent.get_choice(b3))
