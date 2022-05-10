# Implementation of the Feudal board game with some move restriction
from itertools import combinations
from copy import deepcopy
import random
import multiprocessing


def external_count_moves(pieces_combo, board):
    piece = pieces_combo[0]
    friendly_locs, opponent_locs = board.get_locations(piece.color)
    # Base case:
    if len(pieces_combo) == 1:
        return piece.get_num_moves(board, friendly_locs, opponent_locs)
    else: # Recursion
        count = 0
        for move in piece.get_moves(board, friendly_locs, opponent_locs):
            new_board = board.clone()
            if not new_board.apply_move(piece.location,
                    move, piece.color):
                raise RuntimeError("Could not apply in count_moves")
            count += external_count_moves(pieces_combo[1:], new_board)
        return count


class Board():
    # @param num_moves_permitted    The number of pieces a player can move in
    #                               a single turn. NOTE: This will be
    #                               incremented by 1 and stored for use in
    #                               range() calls.
    def __init__(self, num_moves_permitted=2):
        self.moves_max = num_moves_permitted + 1
        self.rough = set()
        self.mountains = set()
        self.blue_pieces = dict() # MAY BE REVISED # PIECES -> LOCATIONS
        self.blue_pieces_locations = dict() # LOCATIONS -> PIECES
        self.brown_pieces = dict() # MAY BE REVISED # PIECES -> LOCATIONS
        self.brown_pieces_locations = dict() # LOCATIONS -> PIECES
        # Tuple of tuples, first is green, second is interior
        self.blue_castle = [None, None]
        self.brown_castle = [None, None]
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
    def clone(self):
        new_board = Board(self.moves_max - 1)
        new_board.rough = self.rough.copy()
        new_board.mountains = self.mountains.copy()
        # new_board.blue_pieces = deepcopy(self.blue_pieces)
        new_board.blue_pieces = {p.clone() : p.location for p in self.blue_pieces}
        new_board.blue_pieces_locations = {loc : piece for piece, loc in new_board.blue_pieces.items()}
        #new_board.blue_pieces_locations = deepcopy(self.blue_pieces_locations)
        # new_board.brown_pieces = deepcopy(self.brown_pieces)
        new_board.brown_pieces = {p.clone() : p.location for p in self.brown_pieces}
        new_board.brown_pieces_locations = {loc : piece for piece, loc in new_board.brown_pieces.items()}
        # new_board.brown_pieces_locations = deepcopy(self.brown_pieces_locations)
        new_board.blue_castle = self.blue_castle[:]
        new_board.brown_castle = self.brown_castle[:]
        new_board.blue_piece_counts = self.blue_piece_counts.copy()
        new_board.brown_piece_counts = self.brown_piece_counts.copy()

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

    # Loss conditions: all royalty eliminated OR enemy in castle
    def blue_lost(self):
        royalty_eliminated = ((0 == self.blue_piece_counts["king"]) and
            (0 == self.blue_piece_counts["prince"]) and
            (0 == self.blue_piece_counts["duke"]))

        enemy_in_castle = self.blue_castle[1] in self.brown_pieces_locations
        return royalty_eliminated or enemy_in_castle

    def brown_lost(self):
        royalty_eliminated = ((0 == self.brown_piece_counts["king"]) and
            (0 == self.brown_piece_counts["prince"]) and
            (0 == self.brown_piece_counts["duke"]))

        enemy_in_castle = self.brown_castle[1] in self.blue_pieces_locations
        return royalty_eliminated or enemy_in_castle

    def game_over(self):
        return self.brown_lost() or self.blue_lost()

    # Function for adding a single piece to the board
    # Checks for valid placement - i.e. no units placed off the board or on
    # mountains; also checks squire 
    # @return   True if placed successfully, else False
    def add_piece(self, dict_pieces, dict_locations, castle, color, counts,
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
            castle = self.blue_castle if "blue" == color else self.brown_castle
            castle[0] = location
            counts["castle_green"] += 1
            if location in self.mountains:
                self.mountains.remove(location)
            if location in self.rough:
                self.rough.remove(location)
        elif piece_type == "castle_interior":
            castle = self.blue_castle if "blue" == color else self.brown_castle
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
            p = Pikemen(counts["pikemen"] + 1, color, location)
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

    def remove_piece(self):
        pass

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
            bounds = (12,23)
            for loc in configuration.values():
                if type(loc) == list:
                    for loc_sub in loc:
                        if loc_sub[0] < bounds[0] or loc_sub[0] > bounds[1]:
                            return False
                else:
                    if loc[0] < bounds[0] or loc[1] > bounds[1]:
                        return False
            dp = self.brown_pieces
            dl = self.brown_pieces_locations
            c = self.brown_castle
            counts = self.brown_piece_counts
        elif color == "blue":
            bounds = (0,11)
            for loc in configuration.values():
                if type(loc) == list:
                    for loc_sub in loc:
                        if loc_sub[0] < bounds[0] or loc_sub[0] > bounds[1]:
                            return False
                else:
                    if loc[0] < bounds[0] or loc[0] > bounds[1]:
                        return False
            dp = self.blue_pieces
            dl = self.blue_pieces_locations
            c = self.blue_castle
            counts = self.blue_piece_counts


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

    def get_pieces(self, color):
        if "blue" == color:
            return self.blue_pieces
        else:
            return self.brown_pieces

    # @return get friendly, opponent locations
    def get_locations(self, color):
        if "blue" == color:
            return self.blue_pieces_locations, self.brown_pieces_locations
        else:
            return self.brown_pieces_locations, self.blue_pieces_locations

    def get_counts(self, color):
        if "blue" == color:
            return self.blue_piece_counts
        else:
            return self.brown_piece_counts

    # NOTE: DOES NOT REPLICATE A UNIFORM DISTRIBUTION OVER ALL POSSIBLE MOVES
    def get_random_move(self, color):
        # Reference the correct set of pieces
        pieces = self.get_pieces(color)

        # 1. Select how many pieces to move
        # Take the min between 4 and the number of pieces remaining (we add
        # 1 to each below because range is exclusive of the second number)
        # TODO: Should we be weighting 1,2,3,or 4 pieces differently
        num_pieces = random.randrange(1, min(self.moves_max, len(pieces) + 1))

        # For consistency with what are actually possible moves, we must
        # repeatedly try creating a random move until one where all chosen
        # pieces have moved is generated
        incomplete = True
        while incomplete:
            # 2. Choose pieces
            chosen_pieces = random.sample(pieces.keys(), k=num_pieces)

            # 3. Try returning a play where all of these pieces have moved
            final_board = self.clone()
            sorted_pieces = sorted(chosen_pieces)
            final_moves = []
            for i in range(num_pieces):
                curr_piece = sorted_pieces[i]
                temp = final_board.clone()
                f_locs, o_locs = temp.get_locations(color)
                piece_move = curr_piece.get_random_piece_move(temp, f_locs,
                    o_locs)
                # If a piece is not able to move, abandon this generation
                if piece_move is None:
                    break
                final_moves.append((curr_piece.location, piece_move))
                if not final_board.apply_move(curr_piece.location, piece_move,
                    color):
                        raise RuntimeError(
                            "get_random_move: move not successfully applied")
                # If all chosen pieces have been successfully moved...
                if i == (num_pieces-1):
                    incomplete = False

        # Form of ([(first_piece_start, first_piece_new)...], board)
        return (final_moves, final_board)


    def count_moves(self, pieces_combo, board):
        piece = pieces_combo[0]
        friendly_locs, opponent_locs = board.get_locations(piece.color)
        # Base case:
        if len(pieces_combo) == 1:
            return piece.get_num_moves(board, friendly_locs, opponent_locs)
        else: # Recursion
            count = 0
            for move in piece.get_moves(board, friendly_locs, opponent_locs):
                new_board = board.clone()
                if not new_board.apply_move(piece.location,
                        move, piece.color):
                    raise RuntimeError("Could not apply in count_moves")
                count += self.count_moves(pieces_combo[1:], new_board)
            return count

    # Count moves but pass the board by reference,
    # undo every move after recursive calls.
    def count_moves_ref(self, pieces_combo, board):
        piece = pieces_combo[0]
        friendly_locs, opponent_locs = board.get_locations(piece.color)
        # Base case:
        if len(pieces_combo) == 1:
            return piece.get_num_moves(board, friendly_locs, opponent_locs)
        else: # Recursion
            count = 0
            for move in piece.get_moves(board, friendly_locs, opponent_locs):
                save = board.apply_move(piece.location,move, piece.color)
                count += self.count_moves(pieces_combo[1:], board)
                board.reverse_apply_move(save,piece.color)
            return count

    # Recursive get_num_all_moves to calculate number of possible moves given 
    # the current board configuration.
    def get_num_all_moves(self, color):
        pieces = self.get_pieces(color)
        # friendly_locs, opponent_locs = self.get_locations(color)
        count = 0

        for i in range(1, self.moves_max):
            for pieces_combo in combinations(pieces.keys(), i):
                count += self.count_moves(sorted(pieces_combo), self.clone())

        # Pass board by reference approach.
        #for i in range(1,4):
        #    for pieces_combo in combinations(pieces.keys(), i):
        #        count += self.count_moves_ref(sorted(pieces_combo), self)

        # Parallel approach
        # with multiprocessing.Pool(processes=8) as pool:
        #     for i in range(1,3):
        #         count += sum(pool.starmap(external_count_moves, [(sorted(p_combo), self.clone()) for p_combo in combinations(pieces.keys(), i)]))

        # For all single piece moves...
        # for piece in pieces:
        #     count += piece.get_num_moves(self.clone(), friendly_locs, opponent_locs)

        # # # NEED TO HANDLE MOVES OF 2,3,4 PIECES...
        # for combo in combinations(pieces.keys(), 2):
        #     first_piece, second_piece = sorted(combo)
        #     for move in first_piece.get_moves(self, friendly_locs, opponent_locs):
        #         new_board = self.clone()
        #         if not new_board.apply_move(first_piece.location,
        #                 move, first_piece.color):
        #             raise RuntimeError("Could not apply in count_moves")
        #         new_f_locs, new_o_locs = new_board.get_locations(first_piece.color)
        #         count += second_piece.get_num_moves(new_board, new_f_locs, new_o_locs)

        return count


    # Recursive function to generate all moves for a given piece combination and board.
    def get_moves(self, pieces_combo, board, moves_list):
        piece = pieces_combo[0]
        friendly_locs, opponent_locs = board.get_locations(piece.color)
        # Base case:
        if len(pieces_combo) == 1:
            for move in piece.get_moves(board.clone(), friendly_locs, opponent_locs):
                new_board = board.clone()
                if not new_board.apply_move(piece.location,move, piece.color):
                    raise RuntimeError("Could not apply in count_moves")        
                moves_list.append((piece.location, move))
                yield (moves_list[:], new_board)
                moves_list.pop()
        else: # Recursion
            for move in piece.get_moves(board, friendly_locs, opponent_locs):
                new_board = board.clone()
                if not new_board.apply_move(piece.location,move, piece.color):
                    raise RuntimeError("Could not apply in count_moves")
                
                moves_list.append((piece.location, move))
                yield from self.get_moves(pieces_combo[1:], 
                                          new_board, 
                                          moves_list[:])
                moves_list.pop()

    # Pass by reference analogue to get_moves. 
    # This function is called by get_all_moves_ref()
    def get_moves_ref(self, pieces_combo, board, moves_list, all_moves):
        piece = pieces_combo[0]
        friendly_locs, opponent_locs = board.get_locations(piece.color)
        # Base case:
        if len(pieces_combo) == 1:
            for move in piece.get_moves_list(board, friendly_locs, opponent_locs):
                moves_list.append((piece.location, move))
                all_moves.append(moves_list[:])
                moves_list.pop()
        else: # Recursion
            for move in piece.get_moves_list(board, friendly_locs, opponent_locs):
                moves_list.append((piece.location, move))
                save = board.apply_move_retState(piece.location, move, piece.color)
                board.get_moves_ref(pieces_combo[1:], board, moves_list, all_moves)
                board.reverse_apply_move(save, piece.color)
                moves_list.pop()

    # get_all_moves_ref - generate all moves but pass around the same 
    # board copy. 
    def get_all_moves_ref(self, color):
        if "blue" == color:
            pieces = self.blue_pieces
            friendly_locs = self.blue_pieces_locations
            opponent_locs = self.brown_pieces_locations
        else:
            pieces = self.brown_pieces
            friendly_locs = self.brown_pieces_locations
            opponent_locs = self.blue_pieces_locations

        all_moves = []

        for i in range(1, self.moves_max):
            for pieces_combo in combinations(pieces.keys(), i):
                self.get_moves_ref(sorted(pieces_combo), self, [], all_moves)
        return all_moves

    # Must stitch together all possible moves of all pieces, in proper order...
    # Returning copies of itself where the game has been updated to reflect the
    # consequences of a move
    # yields pairs of (move, board) where board is an updated clone reflecting
    # move, and move is a list of (piece, new_location) tuples
    def get_all_moves(self, color):
        # Reference the correct set of pieces
        if "blue" == color:
            pieces = self.blue_pieces
            friendly_locs = self.blue_pieces_locations
            opponent_locs = self.brown_pieces_locations
        else:
            pieces = self.brown_pieces
            friendly_locs = self.brown_pieces_locations
            opponent_locs = self.blue_pieces_locations

        for i in range(1, self.moves_max):
            for pieces_combo in combinations(pieces.keys(), i):
                yield from self.get_moves(sorted(pieces_combo), self.clone(), [])

        # For all single piece moves...
        #for piece in pieces:
            # For each piece, fetch an available move, apply it, and pass to
            # next piece
        #    for piece_move in piece.get_moves(self.clone(), friendly_locs, opponent_locs):
                #print(piece, piece.location, piece_move)
        #        new_board = self.clone()
        #        if not new_board.apply_move(piece.location, piece_move, color):
        #            raise RuntimeError(
        #                "get_all_moves: move not successfully applied")
        #        yield ([(piece.location, piece_move)],new_board)

        # For all moves of two pieces (if possible)...
        # if len(pieces) >= 2:
        #     for combination in combinations(pieces.keys(), 2):
        #         # The combination must be ordered correctly...
        #         sorted_selection = sorted(combination)

        #         first_piece = sorted_selection[0]
        #         second_piece = sorted_selection[1]
        #         for first_piece_move in first_piece.get_moves(self.clone(), friendly_locs, opponent_locs):
        #             new_board_1 = self.clone()
        #             if not new_board_1.apply_move(first_piece.location, first_piece_move, color):
        #                 print("get_all_moves: move not successfully applied")
        #                 raise RuntimeError("get_all_moves: 1 of 2 move not successfully applied")
        #             for second_piece_move in second_piece.get_moves(new_board_1, friendly_locs, opponent_locs): # THIS IS WRONG
        #                 new_board_2 = new_board_1.clone()
        #                 if not new_board_2.apply_move(second_piece.location, second_piece_move, color):
        #                     print("get_all_moves: move not successfully applied")
        #                     raise RuntimeError("get_all_moves: 2 of 2 move not successfully applied)
        #                 yield([(first_piece.location, first_piece_move),(second_piece.location, second_piece_move)], new_board_2)

    # Apply sequence of moves to the board (1 to 4 moves).
    # TODO: PUT MORE CHECKING
    # @param moves is a list of (piece,loc) tuples, where loc denotes the new location
    #        for the piece.
    def apply_move(self, origin, new_location, color):
        if "blue" == color:
            friendly_pieces = self.blue_pieces
            opponent_pieces = self.brown_pieces
            friendly_locs = self.blue_pieces_locations
            opponent_locs = self.brown_pieces_locations
            opponent_counts = self.brown_piece_counts
        else: # Brown
            friendly_pieces = self.brown_pieces
            opponent_pieces = self.blue_pieces
            friendly_locs = self.brown_pieces_locations
            opponent_locs = self.blue_pieces_locations
            opponent_counts = self.blue_piece_counts

        #print(friendly_locs)
        #print(self.blue_pieces)
        #print(self.blue_pieces_locations)
        current_piece = friendly_locs[origin]
        # If new_location is where an enemy is delete the opponent piece and
        # move current piece
        # Special case: archer
        if new_location in opponent_locs:
            # print(origin, " to ", new_location)
            # self.display()

            # Delete opponent
            enemy_piece = opponent_locs[new_location]
            opponent_counts[str(enemy_piece)] -= 1 # Decrement count
            del opponent_locs[new_location] # Remove from locations -> pieces
            del opponent_pieces[enemy_piece] # Remove from pieces -> locations

            # Move current piece (if not an archer)
            if "archer" != str(current_piece):
                del friendly_locs[origin] # Remove from locations -> pieces
                # Reinsert with correct location
                friendly_locs[new_location] = current_piece
                # Update pieces -> locations
                friendly_pieces[current_piece] = new_location
                # Update the piece itself
                current_piece.location = new_location

            # self.display()
            # print("ATTACKED ABOVE")
            # exit()
        # Otherwise just moving to a new spot
        else:
            del friendly_locs[origin] # Remove from locations -> pieces
            # Reinsert with correct location
            friendly_locs[new_location] = current_piece
            # Update pieces -> locations
            friendly_pieces[current_piece] = new_location
            # Update the piece itself
            current_piece.location = new_location

        return True

    # Apply move and return pre-move state.
    def apply_move_retState(self, origin, new_location, color):
        archer_attack = False
        enemy_piece = None
        if "blue" == color:
            friendly_pieces = self.blue_pieces
            opponent_pieces = self.brown_pieces
            friendly_locs = self.blue_pieces_locations
            opponent_locs = self.brown_pieces_locations
            opponent_counts = self.brown_piece_counts
        else: # Brown
            friendly_pieces = self.brown_pieces
            opponent_pieces = self.blue_pieces
            friendly_locs = self.brown_pieces_locations
            opponent_locs = self.blue_pieces_locations
            opponent_counts = self.blue_piece_counts

        current_piece = friendly_locs[origin]
        # If new_location is where an enemy is delete the opponent piece and
        # move current piece
        # Special case: archer
        if new_location in opponent_locs:
            # Delete opponent
            enemy_piece = opponent_locs[new_location]
            opponent_counts[str(enemy_piece)] -= 1 # Decrement count
            del opponent_locs[new_location] # Remove from locations -> pieces
            del opponent_pieces[enemy_piece] # Remove from pieces -> locations

            archer_attack = True

            # Move current piece (if not an archer)
            if "archer" != str(current_piece):
                del friendly_locs[origin] # Remove from locations -> pieces
                # Reinsert with correct location
                friendly_locs[new_location] = current_piece
                # Update pieces -> locations
                friendly_pieces[current_piece] = new_location
                # Update the piece itself
                current_piece.location = new_location
                archer_attack = False
        # Otherwise just moving to a new spot
        else:
            del friendly_locs[origin] # Remove from locations -> pieces
            # Reinsert with correct location
            friendly_locs[new_location] = current_piece
            # Update pieces -> locations
            friendly_pieces[current_piece] = new_location
            # Update the piece itself
            current_piece.location = new_location
        # Return move coordinates and attacked piece, if any.
        return (origin,new_location,enemy_piece,archer_attack)

    # Given predecessor save state, reverse apply the move for the 
    # board.
    def reverse_apply_move(self, save, color):
        (origin, dest, piece, archer_attack) = save
        if "blue" == color:
            friendly_pieces = self.blue_pieces
            opponent_pieces = self.brown_pieces
            friendly_locs = self.blue_pieces_locations
            opponent_locs = self.brown_pieces_locations
            opponent_counts = self.brown_piece_counts
        else: # Brown
            friendly_pieces = self.brown_pieces
            opponent_pieces = self.blue_pieces
            friendly_locs = self.brown_pieces_locations
            opponent_locs = self.blue_pieces_locations
            opponent_counts = self.blue_piece_counts

        # If we deleted an enemy.
        if piece is not None:
            # If archer attacked, simply set the piece back.
            if archer_attack:
                opponent_locs[dest] = piece
                opponent_pieces[piece] = dest
            # Otherwise move piece at dest to origin, then place enemy piece
            # back.
            else:
                move_back = friendly_locs[dest]
                del friendly_locs[dest]
                friendly_locs[origin] = move_back
                friendly_pieces[move_back] = origin
                move_back.location = origin
                opponent_locs[dest] = piece
                opponent_pieces[piece] = dest
            # Increase piece count
            opponent_counts[str(piece)] += 1

        # If we just moved a piece
        else:
            move_back = friendly_locs[dest]
            friendly_locs[origin] = move_back
            friendly_pieces[move_back] = origin
            move_back.location = origin
            del friendly_locs[dest]

    # Apply sequence of moves to board (using apply_move_retState) 
    # and return the save sequence. 
    def apply_moves(self, moves, color):
        saves = []
        # Apply moves to board.
        for move in moves:
            save = self.apply_move_retState(move[0],move[1], color)
            saves.append(save)
        return saves

    def reverse_apply_moves(self, saves, color):
        for i in range(len(saves)-1, -1, -1):
            self.reverse_apply_move(saves[i], color)

class Piece():
    def __init__(self, name, number, color, location, rank, directions):
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
        if directions == None:
            self.directions = [(-1,0),(-1,1),(0,1),(1,1),
                               (1,0),(1,-1),(0,-1),(-1,-1)]
        else:
            self.directions = directions
    # Define less than or equal functionality so that Piece instances can be
    # sorted using Python's sorted() function; this enables us to adhere to the
    # rank (King down to Archer), left-to-right (primary method of
    # tie-breaking among units of the same type) and unit number (secondary
    # method of tie-breaking among units of the same type) move ordering.
    def __lt__(self, other):
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

    def get_random_piece_move(self, board, friendly_locs, opponent_locs):
            num_available_moves = self.get_num_moves(
                board, friendly_locs, opponent_locs)
            if 0 == num_available_moves:
                return None
            chosen_move_num = random.randrange(1, num_available_moves + 1)

            # Retrieve the move generator and iterate until the move
            # corresponding to that move has been retrieved
            # NOTE: I (Dan) tried making a seek_to_move function which
            # basically just returns the chosen move, but it didn't appear to
            # be any faster than just reusing the generator approach
            generator = self.get_moves(board,
                friendly_locs, opponent_locs)
            for _ in range(chosen_move_num):
                piece_move = next(generator)

            return piece_move

    # Basically a copy of get_moves, but instead of yielding moves, just count
    # the number of options - should be faster than using yield logic
    # @return   The actual number of moves (i.e. not 0 indexed)
    def get_num_moves(self, board, friendly_locs, opponent_locs):
        count = 0
        on_green = (self.location == board.blue_castle[0]   or
                    self.location == board.brown_castle[0])

        for direction in self.directions:
            past_green = False
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
                    (i,j) = self.location
                    if (j-new_loc[1]) in [-1,1]:
                        if i-new_loc[0] > 0:
                            (x,y) = (-1,0)
                        else:
                            (x,y) = (1,0)
                    else:
                        if j-new_loc[1] > 0:
                            (x,y) = (0,-1)
                        else:
                            (x,y) = (0,1)
                    if ((x+i,y+j) in [board.blue_castle[1],
                                      board.brown_castle[1]]):
                        break

                # Check if a mounted unit is encountering rough terrain.
                if self.rank in [2,3,4] and new_loc in board.rough:
                    break


                # Check if a mountain has been hit or a friendly piece
                if (new_loc in board.mountains or
                    new_loc in friendly_locs.keys()):
                    break

                # Entering castle green
                if (new_loc in [board.blue_castle[0], board.brown_castle[0]]):
                    count += 1 # yield new_loc
                    # Archer can shoot past the green, so continue on if
                    # archer:
                    if self.rank == 8:
                        past_green = True
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
                    count += 1 # yield new_loc
                    break

                # Attempting to enter castle illegaly.
                elif (not on_green and
                      new_loc in [board.blue_castle[1],board.brown_castle[1]]):
                    break

                # Check if an opponent has been hit
                if new_loc in opponent_locs.keys():
                    count += 1 # yield new_loc
                    break

                # Archer is past green, traversing empty cell.
                if past_green:
                    continue

                count += 1 # yield new_loc

        return count

    def get_moves(self, board, friendly_locs, opponent_locs):
        return self.get_moves_sub(board, friendly_locs, opponent_locs)

    # TODO: Fix Mounted Piece to not go over mountains/rough terrain
    # TODO: ANY CHANGE APPLIED HERE SHOULD BE EQUALLY APPLIED TO GET_NUM_MOVES
    #       TO ENSURE CORRECT NUMBER OF MOVES RETURNED
    def get_moves_sub(self, board, friendly_locs, opponent_locs):
        on_green = (self.location == board.blue_castle[0]   or 
                    self.location == board.brown_castle[0])
        
        for direction in self.directions:
            past_green = False
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
                    (i,j) = self.location
                    if (j-new_loc[1]) in [-1,1]: 
                        if i-new_loc[0] > 0:
                            (x,y) = (-1,0)
                        else:
                            (x,y) = (1,0)
                    else:
                        if j-new_loc[1] > 0:
                            (x,y) = (0,-1)
                        else:
                            (x,y) = (0,1)
                    if ((x+i,y+j) in [board.blue_castle[1],
                                      board.brown_castle[1]]):
                        break

                # Check if a mounted unit is encountering rough terrain.
                if self.rank in [2,3,4] and new_loc in board.rough:
                    break


                # Check if a mountain has been hit or a friendly piece
                if (new_loc in board.mountains or 
                    new_loc in friendly_locs.keys()):
                    break
                
                # Entering castle green
                if (new_loc in [board.blue_castle[0], board.brown_castle[0]]):
                    yield new_loc
                    # Archer can shoot past the green, so continue on if 
                    # archer:
                    if self.rank == 8:
                        past_green = True
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
                
                # Archer is past green, traversing empty cell.
                if past_green:
                    continue

                yield new_loc

    # A copy of get_moves except that it calls get_moves_sub_w_avg
    def get_moves_w_avg(self, board, friendly_locs, opponent_locs):
        return self.get_moves_sub_w_avg(board, friendly_locs, opponent_locs)

    # TODO: Fix Mounted Piece to not go over mountains/rough terrain
    # A copy of get_moves_sub except that this also returns "avenging" moves
    # - i.e. locations of friendly pieces - instead of just breaking upon
    # finding a friendly.
    def get_moves_sub_w_avg(self, board, friendly_locs, opponent_locs):
        on_green = (self.location == board.blue_castle[0]   or
                    self.location == board.brown_castle[0])

        for direction in self.directions:
            past_green = False
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
                    (i,j) = self.location
                    if (j-new_loc[1]) in [-1,1]:
                        if i-new_loc[0] > 0:
                            (x,y) = (-1,0)
                        else:
                            (x,y) = (1,0)
                    else:
                        if j-new_loc[1] > 0:
                            (x,y) = (0,-1)
                        else:
                            (x,y) = (0,1)
                    if ((x+i,y+j) in [board.blue_castle[1],
                                      board.brown_castle[1]]):
                        break

                # Check if a mounted unit is encountering rough terrain.
                if self.rank in [2,3,4] and new_loc in board.rough:
                    break


                # Check if a mountain has been hit or a friendly piece
                if new_loc in board.mountains:
                    break

                # RETURN THE AVENGING MOVE, THEN BREAK
                if new_loc in friendly_locs.keys():
                    yield new_loc
                    break

                # Entering castle green
                if (new_loc in [board.blue_castle[0], board.brown_castle[0]]):
                    yield new_loc
                    # Archer can shoot past the green, so continue on if
                    # archer:
                    if self.rank == 8:
                        past_green = True
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

                # Archer is past green, traversing empty cell.
                if past_green:
                    continue

                yield new_loc

    # TODO: Fix Mounted Piece to not go over mountains/rough terrain
    # TODO: ANY CHANGE APPLIED HERE SHOULD BE EQUALLY APPLIED TO GET_NUM_MOVES
    #       TO ENSURE CORRECT NUMBER OF MOVES RETURNED
    #   get moves but return a list instead of generating.
    def get_moves_list(self, board, friendly_locs, opponent_locs):
        
        res = []
        
        on_green = (self.location == board.blue_castle[0]   or 
                    self.location == board.brown_castle[0])
        
        for direction in self.directions:
            past_green = False
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
                    (i,j) = self.location
                    if (j-new_loc[1]) in [-1,1]: 
                        if i-new_loc[0] > 0:
                            (x,y) = (-1,0)
                        else:
                            (x,y) = (1,0)
                    else:
                        if j-new_loc[1] > 0:
                            (x,y) = (0,-1)
                        else:
                            (x,y) = (0,1)
                    if ((x+i,y+j) in [board.blue_castle[1],
                                      board.brown_castle[1]]):
                        break

                # Check if a mounted unit is encountering rough terrain.
                if self.rank in [2,3,4] and new_loc in board.rough:
                    break


                # Check if a mountain has been hit or a friendly piece
                if (new_loc in board.mountains or 
                    new_loc in friendly_locs.keys()):
                    break
                
                # Entering castle green
                if (new_loc in [board.blue_castle[0], board.brown_castle[0]]):
                    res.append(new_loc)
                    # Archer can shoot past the green, so continue on if 
                    # archer:
                    if self.rank == 8:
                        past_green = True
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
                    res.append(new_loc)
                    break

                # Attempting to enter castle illegaly.
                elif (not on_green and 
                      new_loc in [board.blue_castle[1],board.brown_castle[1]]):
                    break

                # Check if an opponent has been hit
                if new_loc in opponent_locs.keys():
                    res.append(new_loc)
                    break
                
                # Archer is past green, traversing empty cell.
                if past_green:
                    continue

                res.append(new_loc)
        return res

class King(Piece):
    def __init__(self, color, location):
        self.multipliers = 2
        super().__init__("KG", "", color, location, 1, None)

    def __str__(self):
        return "king"

    def clone(self):
        return King(self.color, self.location)

class Prince(Piece):
    def __init__(self, color, location):
        self.multipliers = 54
        super().__init__("PR", "", color, location, 2, None)

    def __str__(self):
        return "prince"

    def clone(self):
        return Prince(self.color, self.location)

class Duke(Piece):
    def __init__(self, color, location):
        self.multipliers = 54
        super().__init__("DK", "", color, location, 3, None)

    def __str__(self):
        return "duke"

    def clone(self):
        return Duke(self.color, self.location)

class Knight(Piece):
    def __init__(self, number, color, location):
        self.multipliers = 54
        super().__init__("K", number, color, location, 4, None)

    def __str__(self):
        return "knight"

    def clone(self):
        return Knight(self.number, self.color, self.location)

class Sergeant(Piece):
    def __init__(self, number, color, location):
        self.number = number
        self.multipliers = 12
        super().__init__("S", number, color, location, 5, None)

    def __str__(self):
        return "sergeant"

    def clone(self):
        return Sergeant(self.number, self.color, self.location)

class Pikemen(Piece):
    def __init__(self, number, color, location):
        self.number = number
        self.multipliers = 12
        super().__init__("P", number, color, location, 6, None)

    def __str__(self):
        return "pikemen"

    def clone(self):
        return Pikemen(self.number, self.color, self.location)

class Squire(Piece):
    def __init__(self, color, location):
        self.multipliers = 1
        self.directions = [(-1,-2),(-2,-1), (-2,1), (-1,2),
                            (1,2), (2,1), (2,-1), (1,-2)]
        super().__init__("SQ", "", color, location, 7, self.directions)

    def __str__(self):
        return "squire"

    def clone(self):
        return Squire(self.color, self.location)

class Archer(Piece):
    def __init__(self, color, location):
        self.multipliers = 3
        super().__init__("AR", "", color, location, 8, None)

    def __str__(self):
        return "archer"

    def clone(self):
        return Archer(self.color, self.location)






