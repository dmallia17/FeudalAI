from Board import *

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain.txt")

    # CONVENTION FOR NOW: BLUE TOP(0,11), BROWN BOTTOM(12,23)

    blue_config = {
                    "castle_green" : (1,1), 
                    "castle_interior" : (1,2),
                    "king" : (4,4), 
                    "prince" : (5,5), 
                    "duke" : (6,6), 
                    "knight": [(7,1), (7,2)],
                    "sergeant" : [(8,1),(8,2)],
                    "pikemen" : [(9,12),(9,13), (9,14), (9,15)], 
                    "squire" : (9,7), 
                    "archer" : (1,1)
                    }
    
    brown_config = {
                    "castle_green" : (20,0), 
                    "castle_interior" : (20,1),
                    "king" : (22,22), 
                    "prince" : (18,17), 
                    "duke" : (14,23), 
                    "knight": [(15,23),(15,22)], 
                    "sergeant" : [(16,23),(16,22)],
                    "pikemen" : [(19,0),(19,1),(19,2),(19,3)], 
                    "squire" : (23,23), 
                    "archer" : (22,23)
                    }

    b.place_pieces("blue", blue_config)
    b.place_pieces("brown", brown_config)
    # print("PIECES:\n",b.blue_pieces)
    # print("PIECES_LOCATIONS:\n",b.blue_pieces_locations)
    # print("PIECES_COUNTS:\n",b.blue_piece_counts)
    # print("CASTLE:\n",b.blue_castle)
    # print("PIECES:\n",b.brown_pieces)
    # print("PIECES_LOCATIONS:\n",b.brown_pieces_locations)
    # print("PIECES_COUNTS:\n",b.brown_piece_counts)
    # print("BROWN_CASTLE::\n",b.brown_castle)

    b.display()
    b.display_piece_options(b.blue_pieces_locations[(1,1)])
    gen = b.get_all_moves("blue")
    for i in range(20):
        print((next(gen)))
