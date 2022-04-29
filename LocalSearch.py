# Implements base LocalSearch class and all sub-classes

import random

class LocalSearch():
    def get_random_start(self, board, bounds):
        new_config = {"castle_green" : None, "castle_interior" : None,
            "king" : None, "prince" : None, "duke" : None,
            "knight": [None,None], "sergeant" : [None,None],
            "pikemen" : [None,None,None,None], "squire" : None,
            "archer" : None}

        # Place castle interior, then castle green, both randomly (the latter
        # within the allowable neighbor locations)
        all_locations = [(i,j) for i in range(bounds[0], bounds[1]+1)
                               for j in range(24)]
        castle_interior_location = random.choice(all_locations)
        new_config["castle_interior"] = castle_interior_location

        castle_adjacent = []
        ds = [[-1,0],[1,0],[0,-1],[0,1]]
        for d in ds:
            (x,y) = (castle_interior_location[0] + d[0],
                castle_interior_location[1] + d[1])
            if self.in_bounds(x,y, bounds):
                castle_adjacent.append((x,y))

        castle_green_loc = random.choice(castle_adjacent)
        new_config["castle_green"] = castle_green_loc
        all_locations.remove(castle_green_loc)

        # Then place all pieces randomly
        for piece, locations in new_config.items():
            if "castle_interior" == piece or "castle_green" == piece:
                continue

            if type(locations) == list:
                new_list = []
                for _ in locations:
                    piece_location = random.choice(all_locations)
                    while not self.valid_choice(piece, piece_location, (castle_green_loc, castle_interior_location), board):
                        piece_location = random.choice(all_locations)
                    new_list.append(piece_location)
                    all_locations.remove(piece_location)

                new_config[piece] = new_list
            else:
                piece_location = random.choice(all_locations)
                while not self.valid_choice(piece, piece_location, (castle_green_loc, castle_interior_location), board):
                    piece_location = random.choice(all_locations)
                new_config[piece] = piece_location
                all_locations.remove(piece_location)

        return new_config

    # def strip_terain(self, board, location):
    #     if location in board.mountains:
    #         board.mountains.remove(location)
    #     if location in board.rough:
    #         board.rough.remove(location)

    def in_bounds(self, x, y, bounds):
            return ((x >= bounds[0]) and (x <= bounds[1])
                and (y >= 0) and (y <= 23))

    # @param castle is a tuple of green, interior
    def valid_choice(self, piece, location, castle, board):
        if location in board.mountains and location not in castle:
            return False

        if (piece in ["prince", "duke", "knight"] and 
            location in board.rough and location not in castle):
            return False

        if (piece in ["archer", "squire"] and location == castle[1]):
            return False

        return True

    def get_successor_states(self, config, board, bounds):
        successors = [] # Each successor is a configuration
        temp = list(config.values())
        current_piece_locations = []
        for loc in temp:
            if type(loc) == list:
                for sub_loc in loc:
                    current_piece_locations.append(sub_loc)
            else:
                current_piece_locations.append(loc)

        all_possible_locations = [(i,j)
            for i in range(bounds[0], bounds[1]+1) \
            for j in range(24) if (i,j) not in current_piece_locations]


        for piece, locations in config.items():
            # Don't treat castle green separately
            if "castle_green" == piece:
                continue

            # Special case
            if "castle_interior" == piece:
                # Filter to locations that have an adjacent space
                def filter_green(castle_location):
                    ds = [[-1,0],[1,0],[0,-1],[0,1]]
                    for d in ds:
                        (x,y) = (d[0] + castle_location[0], d[1] + castle_location[1])
                        if self.in_bounds(x,y,bounds) and (x,y) not in current_piece_locations:
                            return True
                    return False 
                all_possible_locations = filter(filter_green, all_possible_locations)
                for loc in all_possible_locations:
                    
                
                
            else: # All other pieces
                if type(locations) == list:
                    # FINISH THIS
                else:
                    # Filter to appropriate new locations for piece
                    new_locations = [loc for loc in all_possible_locations \
                        if self.valid_choice(piece, locations,
                        (config["castle_green"], config["castle_interior"]),
                        board)]
                    # For each possible new location, create a new config where
                    # that piece has been moved there, and append to
                    # successors
                    for loc in new_locations:
                        successor_config = config.copy()
                        successor_config[piece] = loc
                        successors.append(successor_config)

        return successors


    def evaluate_config(self, board):
        return self.ways_onto_castle_green(board)

    ##########################
    ####### HEURISTICS #######
    ##########################
    # Number of ways on to the castle green (max 7)
    # NOTE: May want to count "half a way onto the green" if there is rough
    # terrain, as only mounted units would be forbidden from using this
    # approach
    def ways_onto_castle_green(self, board):
        pass

    # Some measure of royalty being protected / "avengeable"

    # Some measure of king, squire, archer near each other and the castle
    
    # Some measure of coverage of the enemy side of the board (max = 12 * 24?)

    # Some measure of total pieces "avengeable"

    # Some notion of flanks being covered or board control (or both?)



class HillClimbing(LocalSearch):
    def get_piece_placement(self):
        pass

    def choose_successor(self):
        pass


class HillClimbingGreedy(HillClimbing):
    def choose_successor(self):
        pass


