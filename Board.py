# Implementation of the Feudal board game with some move restriction
# Test commit message.
class Board():
    def __init__(self):
        self.rough = set()
        self.mountains = set()
        self.blue_pieces = dict() # MAY BE REVISED
        self.blue_pieces_locations = dict()
        self.brown_pieces = dict() # MAY BE REVISED
        self.brown_pieces_locations = dict()
        # Tuple of tuples, first is green, second is interior
        self.blue_castle = None
        self.brown_castle = None

    # Return a clone of the Board instance, only copying the piece dictionaries
    # TODO: MAKE SURE ALL CLASS MEMBERS ARE CLONED PROPERLY HERE
    def clone(self):
        new_board = Board()
        new_board.rough = self.rough
        new_board.mountains = self.mountains
        new_board.blue_pieces = self.blue_pieces.copy()
        new_board.blue_pieces_locations = self.blue_pieces_locations.copy()
        new_board.brown_pieces = self.brown_pieces.copy()
        new_board.brown_pieces_locations = self.brown_pieces_locations.copy()
        return new_board

    # Parse terrain file and store it in internal representation.
    def parse_terrain(self, filename):
        with open(filename) as file:
            lines = file.readlines()

        parsed_board = [line.split("  ") for line in lines]
        for i in range(len(parsed_board)):
            for j in range(len(parsed_board[i])):
                # Simplistic checking if character in split string (thus
                # ignores newline characters)
                if "#" in parsed_board[i][j]:
                    self.rough.update({(i,j)})
                elif "^" in parsed_board[i][j]:
                    self.mountains.update({(i,j)})

    # TODO: ADD RENDERING OF ALL PIECES - DAN
    # Print board to terminal
    def display(self):
        #cTemp = "\x1b[%dm%7s\x1b[0m "
        #\u001b[4m
        print("     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ")
        for i in range(24):
            print(str(i).ljust(2, " ") + "| ", end="")
            for j in range(24):
                # Print terrain, if relevant
                # CYAN == CASTLE GREEN
                if (i,j) == self.brown_castle[0] or (i,j) == self.blue_castle[0]:
                    print("\x1b[46m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                # RED == CASTLE INTERIOR
                elif (i,j) == self.brown_castle[1] or (i,j) == self.blue_castle[1]:
                    print("\x1b[41m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                # ROUGH == WHITE
                elif (i,j) in self.rough:
                    print("\x1b[47m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                # MOUNTAIN == GREEN
                elif (i,j) in self.mountains:
                    print("\x1b[42m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")

                else:
                    print("\x1b[100m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")

                # Print piece, if relevant

            print("|"+str(i))

        print("     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ")


    # FOR DEBUGGING HELP
    def display_piece_options(self, piece):
        if piece.color == "blue":
            friendlies = self.blue_pieces_locations
            opponents = self.brown_pieces_locations
            color = 94
        else:
            friendlies = self.brown_pieces_locations
            opponents = self.blue_pieces_locations
            color = 33

        new_locs = list(piece.getMoves(self.clone(), friendlies, opponents))
        curr_loc = piece.location

        #cTemp = "\x1b[%dm%7s\x1b[0m "
        #\u001b[4m
        print("     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ")
        for i in range(24):
            print(str(i).ljust(2, " ") + "| ", end="")
            for j in range(24):

                if (i,j) in self.rough and (i,j) == curr_loc:
                    print("\x1b[47;%dm\x1b[4m\x1b[2m \x1b[22mH\x1b[2m \x1b[0m" % color, end="")
                elif (i,j) in self.rough and (i,j) in new_locs:
                    print("\x1b[47;%dm\x1b[4m\x1b[2m \x1b[22mX\x1b[2m \x1b[0m" % color, end="")
                elif (i,j) in self.rough:
                    print("\x1b[47m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                elif (i,j) in self.mountains:
                    print("\x1b[42m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                else:
                    if (i,j) == curr_loc:
                        print("\x1b[100;%dm\x1b[4m\x1b[2m \x1b[22mH\x1b[2m \x1b[0m" % color, end="")
                    elif (i,j) in new_locs:
                        print("\x1b[100;%dm\x1b[4m\x1b[2m \x1b[22mX\x1b[2m \x1b[0m" % color, end="")
                    else:
                        print("\x1b[100m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")

                # Print piece, if relevant

            print("|"+str(i))

        print("     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ")

    def gameover(self, ):
        pass

    # Given a chosen configuration, insert the pieces into the mappings
    def place_pieces(self,):
        pass

    # Must stitch together all possible moves of all pieces, in proper order...
    # Returning copies of itself where the game has been updated to reflect the
    # consequences of a move
    def getAllMoves(self, ):
        pass



class Piece():
    def __init__(self, name, number, color, location):
        if color == "blue":
            self.rep = "\x1b[94m" + name + str(number) + "\x1b[97m"
        else:
            self.rep = "\x1b[33m" + name + str(number) + "\x1b[97m"
        self.location = location
        self.color = color

    def __str__(self):
        return self.rep


class King(Piece):
    def __init__(self, color, location):
        super().__init__("KG", "", color, location)
        self.num = 1

    def __le__(self, other):
        return True

    # TO-DO: ACCOUNT FOR CASTLE DYNAMICS
    def getMoves(self, board, friendly_locs, opponent_locs):
        on_green = (self.location == board.blue_castle[0] or \
            self.location == board.brown_castle[0])
        for direction in [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]:
            for multiplier in [1,2]:
                new_loc = (self.location[0] + direction[0]*multiplier,
                    self.location[1] + direction[1]*multiplier)
                # Check location on board
                if new_loc[0] >= 0 and new_loc[0] <= 23 and \
                    new_loc[1] >= 0 and new_loc[1] <= 23:

                    # Entering castle green
                    if new_loc == board.blue_castle[0] or board.brown_castle[0]:
                        yield new_loc
                        break

                    # Attempting to enter castle interior
                    if on_green and (new_loc == board.blue_castle[1] or board.brown_castle[1]):
                        yield new_loc
                        break
                    elif (not on_green) and (new_loc == board.blue_castle[1] or board.brown_castle[1]):
                        break

                    # Check if a mountain has been hit or a friendly piece
                    if new_loc in board.mountains or \
                        new_loc in friendly_locs.values():
                        break

                    # Check if an opponent has been hit
                    if new_loc in opponent_locs.values():
                        yield new_loc
                        break

                    yield new_loc


class Mounted(Piece):
    # DAN
    def getMoves(self):
        pass


class Prince(Mounted):
    def __init__(self, color, location):
        super().__init__("PR", "", color, location)
        self.num = 2

    def __le__(self, other):
        if self.num < other.num:
            return True
        else:
            return False

class Duke(Mounted):
    def __init__(self, color, location):
        super().__init__("D", "", color, location)
        self.num = 3
    
    def __le__(self, other):
        if self.num < other.num:
            return True
        else:
            return False

class Knight(Mounted):
    def __init__(self, number, color, location):
        super().__init__("K", number, color, location)
        self.num = 4
        self.number = number

    def __le__(self, other):
        if self.num < other.num:
            return True
        elif self.num == other.num:
            if self.location[1] < other.location[1]:
                return True
            elif self.location[1] == other.location[1]:
                return (self.number < other.number)
            else:
                return False
        else:
            return False

# Artjom
class Sergeant(Piece):
    def __init__(self, number, color, location):
        super().__init__("S", number, color, location)
        self.num = 5
        self.number = number

    def __le__(self, other):
        if self.num < other.num:
            return True
        elif self.num == other.num:
            if self.location[1] < other.location[1]:
                return True
            elif self.location[1] == other.location[1]:
                return (self.number < other.number)
            else:
                return False
        else:
            return False

# Artjom
class Pikemen(Piece):
    def __init__(self, number, color, location):
        super().__init__("P", number, color, location)
        self.num = 6
        self.number = number

    def __le__(self, other):
        if self.num < other.num:
            return True
        elif self.num == other.num:
            if self.location[1] < other.location[1]:
                return True
            elif self.location[1] == other.location[1]:
                return (self.number < other.number)
            else:
                return False
        else:
            return False

# Artjom
class Squire(Piece):
    def __init__(self, color, location):
        super().__init__("SQ", "", color, location)
        self.num = 7
    
    def __le__(self, other):
        if self.num < other.num:
            return True
        else:
            return False
# Artjom
class Archer(Piece):
    def __init__(self, color, location):
        super().__init__("A", "", color, location)
        self.num = 8

    def __le__(self, other):
        return False


