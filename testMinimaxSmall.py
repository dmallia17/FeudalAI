from Board import *
from Minimax import *


if __name__ == "__main__":
    b3 = Board()
    b3.parse_terrain("cage_terrain.txt")
    blue_searcher = HillClimbingFirstChoice(b3, "blue")
    brown_searcher = HillClimbingFirstChoice(b3, "brown")

    blue_config = {
        "king": (11,16)
    }

    brown_config = {
        "king": (12,16)
    }

    b3.place_some_pieces("blue", blue_config)
    b3.place_some_pieces("brown", brown_config)
    b3.display()
    
    agent = Minimax_Agent("brown", 5.0, None,None,None)

    print(agent.get_choice(b3))
