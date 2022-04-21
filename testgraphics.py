from Board import *

if __name__ == "__main__":
    b = Board()
    b.parse_terrain("terrain.txt")
    myking = King("blue", (1,1))
    myknight = Knight(1, "brown", (2,2))
    b.blue_pieces[myking] = (1,1)
    b.blue_pieces_locations[(1,1)] = myking
    b.brown_pieces[myknight] = (2,2)
    b.brown_pieces_locations[(2,2)] = myknight
    b.display()
