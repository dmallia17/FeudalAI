# Implementation of the Feudal board game with some move restriction

class Board():
    def __init__(self):
        self.rough = set()
        self.mountains = set()
        self.blue_pieces = dict() # MAY BE REVISED # PIECES -> LOCATIONS
        self.blue_pieces_locations = dict() # LOCATIONS -> PIECES
        self.brown_pieces = dict() # MAY BE REVISED # PIECES -> LOCATIONS
        self.brown_pieces_locations = dict() # LOCATIONS -> PIECES
        # Tuple of tuples, first is green, second is interior
        # TODO: These are temporarily fixed coordinates (until piece placement
        #       is implemented).
        self.blue_castle = [(12,15),(12,16)]
        self.brown_castle = [(10,0),(10,1)]
        self.blue_piece_counts = {"castle_green" : 0, "castle_interior" : 0,
            "king" : 0, "prince" : 0, "duke" : 0, "knight": 0, "sergeant" : 0,
            "pikemen" : 0, "squire" : 0, "archer" : 0}
        self.brown_piece_counts = {"castle_green" : 0, "castle_interior" : 0,
            "king" : 0, "prince" : 0, "duke" : 0, "knight": 0, "sergeant" : 0,
            "pikemen" : 0, "squire" : 0, "archer" : 0}
        self.target_counts = {"castle_green" : 1, "castle_interior" : 1,
            "king" : 1, "prince" : 1, "duke" : 1, "knight": 2, "sergeant" : 2,
            "pikemen" : 4, "squire" : 1, "archer" : 1}

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
      
        # Format strings.
        # display_str must first define a background color, determined by the
        # type of "terrain" (castle is treated as terrain)
        # These are numbers 46, 41, 47, 42 or 100
        # Then it establishes underlining (4)
        # This is followed by faint intensity (2), "normal" intensity (22) and
        # faint again so that the center of each cell is highlighted.
        # Last reset is applied to clear formatting handling for the next cell
        display_str = "\x1b[%dm\x1b[4m\x1b[2m \x1b[22m%s\x1b[2m%s\x1b[0m"
        board_nums1 = "     0  1  2  3  4  5  6  7  8  9 "
        board_nums2 = "10 11 12 13 14 15 16 17 18 19 20 21 22 23 "

        # Define a combination of piece dictionaries for checking if a piece
        # should be rendered on the board
        comb_dict = {**self.blue_pieces_locations,
            **self.brown_pieces_locations}

        print(board_nums1 + board_nums2)
        for i in range(24):
            print(str(i).ljust(2, " ") + "| ", end="")
            for j in range(24):
                # Assume no piece present then check
                foreground = "  "
                if (i,j) in comb_dict:
                    foreground = comb_dict[(i,j)].rep

                # CYAN == CASTLE GREEN
                if (i,j) in [self.brown_castle[0], self.blue_castle[0]]:
                    print(display_str % (46, foreground[:-1], foreground[-1]),
                        end="")
                # RED == CASTLE INTERIOR
                elif (i,j) in [self.brown_castle[1], self.blue_castle[1]]:
                    print(display_str % (41, foreground[:-1], foreground[-1]),
                        end="")
                # ROUGH == WHITE
                elif (i,j) in self.rough:
                    print(display_str % (47, foreground[:-1], foreground[-1]),
                        end="")
                # MOUNTAIN == GREEN
                elif (i,j) in self.mountains:
                    print(display_str % (42, foreground[:-1], foreground[-1]),
                        end="")
                # EMPTY TERRAIN == BROWN/GREY.
                else:
                    print(display_str % (100, foreground[:-1], foreground[-1]),
                        end="")
            print("|"+str(i))
        print(board_nums1 + board_nums2)

    # FOR DEBUGGING HELP
    def display_piece_options(self, piece):

        # Format strings.
        board_nums1 = "     0  1  2  3  4  5  6  7  8  9 "
        board_nums2 = "10 11 12 13 14 15 16 17 18 19 20 21 22 23 "

        # Define a combination of piece dictionaries for checking if a piece
        # should be rendered on the board
        comb_dict = {**self.blue_pieces_locations,
            **self.brown_pieces_locations}

        if piece.color == "blue":
            friendlies = self.blue_pieces_locations
            opponents = self.brown_pieces_locations
            color = 94
        else:
            friendlies = self.brown_pieces_locations
            opponents = self.blue_pieces_locations
            color = 33

        new_locs = list(piece.get_moves(self.clone(), friendlies, opponents))
        # curr_loc = piece.location
        display_str = "\x1b[%dm\x1b[4m\x1b[2m \x1b[22m%s\x1b[2m%s\x1b[0m"

        print(board_nums1 + board_nums2)

        for i in range(24):
            print(str(i).ljust(2, " ") + "| ", end="")
            for j in range(24):

                # Assume no piece present then check
                foreground = "  "
                if (i,j) in comb_dict:
                    foreground = comb_dict[(i,j)].rep
                elif (i,j) in new_locs:
                    foreground = "\x1b[91mX "

                # CYAN == CASTLE GREEN
                if (i,j) in [self.brown_castle[0], self.blue_castle[0]]:
                    print(display_str % (46, foreground[:-1], foreground[-1]),
                        end="")
                # RED == CASTLE INTERIOR
                elif (i,j) in [self.brown_castle[1], self.blue_castle[1]]:
                    print(display_str % (41, foreground[:-1], foreground[-1]),
                        end="")
                # ROUGH == WHITE
                elif (i,j) in self.rough:
                    print(display_str % (47, foreground[:-1], foreground[-1]),
                        end="")
                # MOUNTAIN == GREEN
                elif (i,j) in self.mountains:
                    print(display_str % (42, foreground[:-1], foreground[-1]),
                        end="")
                # EMPTY TERRAIN == BROWN/GREY.
                else:
                    print(display_str % (100, foreground[:-1], foreground[-1]),
                        end="")

                # if (i,j) in self.rough and (i,j) == curr_loc:
                #     print("\x1b[47;%dm\x1b[4m\x1b[2m \x1b[22mH\x1b[2m \x1b[0m" % color, end="")
                # elif (i,j) in self.rough and (i,j) in new_locs:
                #     print("\x1b[47;%dm\x1b[4m\x1b[2m \x1b[22mX\x1b[2m \x1b[0m" % color, end="")
                # elif (i,j) in self.rough:
                #     print("\x1b[47m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                # elif (i,j) in self.mountains:
                #     print("\x1b[42m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")
                # else:
                #     if (i,j) == curr_loc:
                #         print("\x1b[100;%dm\x1b[4m\x1b[2m \x1b[22mH\x1b[2m \x1b[0m" % color, end="")
                #     elif (i,j) in new_locs:
                #         print("\x1b[100;%dm\x1b[4m\x1b[2m \x1b[22mX\x1b[2m \x1b[0m" % color, end="")
                #     else:
                #         print("\x1b[100m\x1b[4m\x1b[2m \x1b[22m \x1b[2m \x1b[0m", end="")

                # Print piece, if relevant
            print("|"+str(i))
        print(board_nums1 + board_nums2)

    def gameover(self, ):
        pass

    # Function for adding a single piece to the board
    # Checks for valid placement - i.e. no units placed off the board or on
    # mountains; also checks squire 
    # @return   True if placed successfully, else False
    def add_piece(self, dict_pieces, dict_locations, counts, color, castle,
        piece_type, location):
        # Check in bounds
        if (location[0] < 0  or location[0] > 23 or location[1] < 0 or
            location[1] > 23):
            return False

        # Check if a piece other than the castle is being placed on a mountain
        if ((piece_type != "castle_green" and piece_type != "castle_interior")
            and location in self.mountains):
            return False

        # Check squire and archer not being placd in castle interior
        if ((piece_type == "squire" or piece_type == "archer") and
            location in [self.blue_castle[1], self.brown_castle[1]]):
            return False

        # Otherwise place piece
        if piece_type == "castle_green":
            castle[0] = location
            counts["castle_green"] += 1
            if location in self.mountains:
                self.mountains.remove(location)
            if location in self.rough:
                self.rough.remove(location)
        elif piece_type == "castle_interior":
            castle[1] = location
            counts["castle_interior"] += 1
            if location in self.mountains:
                self.mountains.remove(location)
            if location in self.rough:
                self.rough.remove(location)
        elif piece_type == "king":
            p = King(color, location)
            counts["king"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "prince":
            p = Prince(color, location)
            counts["prince"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "duke":
            p = Duke(color, location)
            counts["duke"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "knight":
            p = Knight(counts["knight"] + 1, color, location)
            counts["knight"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "sergeant":
            p = Sergeant(counts["sergeant"] + 1, color, location)
            counts["sergeant"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "pikemen":
            p = Knight(counts["pikemen"] + 1, color, location)
            counts["pikemen"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "squire":
            p = Squire(color, location)
            counts["squire"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p
        elif piece_type == "archer":
            p = Archer(color, location)
            counts["archer"] += 1
            dict_pieces[p] = location
            dict_locations[location] = p

        return True


    # Given a chosen configuration, handle all piece setup
    # Checks valid placement in terms of field of play (no pieces on other
    # player's side)
    # First places the castle, so that proper checks 
    # @param configuration  Dictionary mapping piece types to locations:
    #                       ex: configuration["knight"] = [(1,1), (2,2)]
    # @return 
    def place_pieces(self, color, configuration):
        # dp = dict_pieces
        # dl = dict_locations
        # c  = castle
        if color == "brown":
            dp = self.brown_pieces
            dl = self.brown_pieces_locations
            c = self.brown_castle
            counts = self.brown_piece_counts
            bounds = (0,11)
        elif color == "blue":
            dp = self.blue_pieces
            dl = self.brown_pieces_locations
            c = self.blue_castle
            counts = self.blue_piece_counts
            bounds = (12,23)

        self.add_piece(dp, dl, c, color, counts,
                        "castle_interior", configuration["castle_interior"]) 
        self.add_piece(dp, dl, c, color, counts,
                        "castle_green", configuration["castle_green"]) 
        self.add_piece(dp, dl, c, color, counts,
                        "king", configuration["king"])
        self.add_piece(dp, dl, c, color, counts,
                        "prince", configuration["prince"])
        self.add_piece(dp, dl, c, color, counts,
                        "duke", configuration["duke"])
        for loc in configuration["knight"]:
            self.add_piece(dp, dl, c, color, counts, "knight", loc)
        for loc in configuration["sergeant"]:
            self.add_piece(dp, dl, c, color, counts, "sergeant", loc)
        for loc in configuration["pikemen"]:
            self.add_piece(dp, dl, c, color, counts, "pikemen", loc)
        self.add_piece(dp, dl, c, color, counts,
                        "squire", configuration["squire"])
        self.add_piece(dp, dl, c, color, counts,
                        "archer", configuration["archer"])

        return counts == self.target_counts


    # Must stitch together all possible moves of all pieces, in proper order...
    # Returning copies of itself where the game has been updated to reflect the
    # consequences of a move
    def get_all_moves(self, ):
        pass

class Piece():
    def __init__(self, name, number, color, location, rank):
        if color == "blue":
            self.rep = "\x1b[94m" + name + str(number)
        else:
            self.rep = "\x1b[33m" + name + str(number)
        self.name = name
        self.number = number
        self.color = color
        self.location = location
        self.rank = rank
        # Default directions (only Squire overrides these).
        self.directions = [(-1,0),(-1,1),(0,1),(1,1),
                           (1,0),(1,-1),(0,-1),(-1,-1)]

    # Define less than or equal functionality so that Piece instances can be
    # sorted using Python's sorted() function; this enables us to adhere to the
    # rank (King down to Archer), left-to-right (primary method of
    # tie-breaking among units of the same type) and unit number (secondary
    # method of tie-breaking among units of the same type) move ordering.
    def __le__(self, other):
        if self.rank < other.rank:
            return True
        elif self.rank == other.rank:
            if self.location[1] < other.location[1]:
                return True
            elif self.location[1] == other.location[1]:
                return (self.number < other.number)
            else:
                return False
        else:
            return False

    def __str__(self):
        return self.rep

    # TODO 1: Add Squire functionality.
    # TODO 2: Test this.
    def get_moves(self, board, friendly_locs, opponent_locs):
        on_green = (self.location == board.blue_castle[0]   or 
                    self.location == board.brown_castle[0])
        
        for direction in self.directions:
            for multiplier in range(1,self.multipliers+1):
                # IF SERGEANT AND MULTIPLIER > 1, stop searching 
                # horizontally and vertically.
                if self.rank == 5:
                    if (direction in [(-1,0),(0,1),(1,0),(0,-1)] and 
                        multiplier > 1):
                        break
                # IF PIKEMAN AND MULTIPLIER > 1, stop searching diagonally.
                if self.rank == 6:
                    if (direction in [(-1,-1),(1,-1),(1,1),(-1,1)] and 
                        multiplier > 1):
                        break
                new_loc = ( self.location[0] + direction[0]*multiplier,
                            self.location[1] + direction[1]*multiplier)
                # Check if location is in bounds.
                if (new_loc[0] < 0  or
                    new_loc[0] > 23 or 
                    new_loc[1] < 0  or
                    new_loc[1] > 23):
                    break

                # Check if squire is jumping over a castle.
                if self.rank == 7:
                    
                    break

                # Check if a mounted unit is encountering rough terrain.
                if self.rank in [2,3,4] and new_loc in board.rough:
                    break

                # Check if a mountain has been hit or a friendly piece
                if (new_loc in board.mountains or 
                    new_loc in friendly_locs.values()):
                    break
                
                # Entering castle green
                if (new_loc in [board.blue_castle[0], board.brown_castle[0]]):
                    yield new_loc
                    # Archer can shoot past the green, so continue on if 
                    # archer:
                    if self.rank == 8:
                        continue
                    break

                # Archers can not enter castle interior.
                if (self.rank == 8  and
                    on_green        and
                    new_loc in [board.blue_castle[1], board.brown_castle[1]]):
                    break

                # Attempting to enter castle interior
                if  (on_green and 
                    new_loc in [board.blue_castle[1], board.brown_castle[1]]):
                    yield new_loc
                    break

                # Attempting to enter castle illegaly.
                elif (not on_green and 
                      new_loc in [board.blue_castle[1],board.brown_castle[1]]):
                    break

                # Check if an opponent has been hit
                if new_loc in opponent_locs.keys():
                    yield new_loc
                    break
                yield new_loc

class King(Piece):
    def __init__(self, color, location):
        self.multipliers = 2
        self.rank = 1
        super().__init__("KG", "", color, location, self.rank)

class Mounted(Piece):
    # DAN
    def __init__(self, name, number, color, location, rank):
        super().__init__(name, number, color, location, rank)


class Prince(Mounted):
    def __init__(self, color, location):
        self.multipliers = 54
        self.rank = 2
        super().__init__("PR", "", color, location, self.rank)

class Duke(Mounted):
    def __init__(self, color, location):
        self.multipliers = 54
        self.rank = 3
        super().__init__("DK", "", color, location, self.rank)
    
class Knight(Mounted):
    def __init__(self, number, color, location):
        self.multipliers = 54
        self.rank = 4
        super().__init__("K", number, color, location, self.rank)

class Sergeant(Piece):
    def __init__(self, number, color, location):
        self.number = number
        self.multipliers = 12
        self.rank = 5
        super().__init__("S", number, color, location, self.rank)

class Pikemen(Piece):
    def __init__(self, number, color, location):
        self.number = number
        self.multipliers = 12
        self.rank = 6
        super().__init__("P", number, color, location, self.rank)

class Squire(Piece):
    def __init__(self, color, location):
        self.multipliers = 1
        self.rank = 7
        self.directions = [(-1,-2),(-2,-1), (-2,1), (-1,2),
                            (1,2), (2,1), (2,-1), (1,-2)]
        super().__init__("SQ", "", color, location, self.rank)
    
class Archer(Piece):
    def __init__(self, color, location):
        self.multipliers = 3
        self.rank = 8
        super().__init__("AR", "", color, location, self.rank)






