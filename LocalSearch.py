# Implements base LocalSearch class and all sub-classes

import random
from copy import deepcopy

class LocalSearch():
    # @param board      an instance of the Board class - only really needed
    #                   for the terrain
    # @param bounds     a tuple of lower and upper row limits (lower = closer
    #                   to top of the board)
    def __init__(self, board, bounds):
        self.board = board
        self.bounds = bounds

    def get_random_start(self):
        new_config = {"castle_green" : None, "castle_interior" : None,
            "king" : None, "prince" : None, "duke" : None,
            "knight": [None,None], "sergeant" : [None,None],
            "pikemen" : [None,None,None,None], "squire" : None,
            "archer" : None}

        # Place castle interior, then castle green, both randomly (the latter
        # within the allowable neighbor locations)
        all_locations = [(i,j) for i in range(self.bounds[0], self.bounds[1]+1)
                               for j in range(24)]
        castle_interior_location = random.choice(all_locations)
        new_config["castle_interior"] = castle_interior_location

        castle_adjacent = []
        ds = [[-1,0],[1,0],[0,-1],[0,1]]
        for d in ds:
            (x,y) = (castle_interior_location[0] + d[0],
                castle_interior_location[1] + d[1])
            if self.in_bounds(x,y):
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
                    while not self.valid_choice(piece, piece_location, (castle_green_loc, castle_interior_location)):
                        piece_location = random.choice(all_locations)
                    new_list.append(piece_location)
                    all_locations.remove(piece_location)

                new_config[piece] = new_list
            else:
                piece_location = random.choice(all_locations)
                while not self.valid_choice(piece, piece_location, (castle_green_loc, castle_interior_location)):
                    piece_location = random.choice(all_locations)
                new_config[piece] = piece_location
                all_locations.remove(piece_location)

        return new_config

    # def strip_terain(self, board, location):
    #     if location in board.mountains:
    #         board.mountains.remove(location)
    #     if location in board.rough:
    #         board.rough.remove(location)

    def in_bounds(self, x, y):
            return ((x >= self.bounds[0]) and (x <= self.bounds[1])
                and (y >= 0) and (y <= 23))

    # @param castle is a tuple of green, interior
    def valid_choice(self, piece, location, castle):
        if location in self.board.mountains and location not in castle:
            return False

        if (piece in ["prince", "duke", "knight"] and 
            location in self.board.rough and location not in castle):
            return False

        if (piece in ["archer", "squire"] and location == castle[1]):
            return False

        return True

    # For finding adjacent locations to a new interior location, where the
    # castle green could be placed
    def green_locs(self, castle_interior_location, current_piece_locations):
        ds = [(-1,0),(1,0),(0,-1),(0,1)]
        locs = []
        for d in ds:
            (x,y) = (d[0] + castle_interior_location[0],
                d[1] + castle_interior_location[1])
            if self.in_bounds(x,y) and \
                (x,y) not in current_piece_locations:
                locs.append((x,y))
        return locs

    def extract_piece_locations(self, config):
        temp = list(config.values())
        current_piece_locations = []
        for loc in temp:
            if type(loc) == list:
                for sub_loc in loc:
                    current_piece_locations.append(sub_loc)
            else:
                current_piece_locations.append(loc)

        return current_piece_locations

    def get_all_possible_locations(self, config):
        return [(i,j)
            for i in range(self.bounds[0], self.bounds[1]+1) \
            for j in range(24) \
                if (i,j) not in self.extract_piece_locations(config)]

    def get_successor_states(self, config):
        successors = [] # Each successor is a configuration
        temp = list(config.values())
        current_piece_locations = self.extract_piece_locations(config)
        all_possible_locations = self.get_all_possible_locations(config)


        for piece, locations in config.items():
            # Don't treat castle green separately
            if "castle_green" == piece:
                continue

            # Special case
            if "castle_interior" == piece:
                # For all possible places to put the interior...
                for loc in all_possible_locations:
                    green_locs = self.green_locs(loc, current_piece_locations)
                    # For all possible places to put the green...
                    # This may be none (empty list) in which case the loc for
                    # the interior will be implicitly abandoned
                    for green_loc in green_locs:
                        successor_config = deepcopy(config)
                        successor_config["castle_interior"] = loc
                        successor_config["castle_green"] = green_loc
                        successors.append(successor_config)
            else: # All other pieces
                # Uncomment the below "continue" to quickly limit testing to
                # castle placement
                # continue
                if type(locations) == list: # Multiple piece types
                    # Filter to appropriate new locations for pieces of this
                    # type
                    new_locations = [loc for loc in all_possible_locations \
                        if self.valid_choice(piece, loc,
                        (config["castle_green"], config["castle_interior"]))]
                    # For each piece, for each possible new location, create a
                    # new config where that piece has been moved there, and
                    # append to successors
                    for i in range(len(locations)):
                        for loc in new_locations:
                            # Must deepcopy, else lists will be linked across
                            # successor configs
                            successor_config = deepcopy(config)
                            successor_config[piece][i] = loc
                            successors.append(successor_config)
                else: # Single piece types
                    # Filter to appropriate new locations for piece
                    new_locations = [loc for loc in all_possible_locations \
                        if self.valid_choice(piece, locations,
                        (config["castle_green"], config["castle_interior"]))]
                    # For each possible new location, create a new config where
                    # that piece has been moved there, and append to
                    # successors
                    for loc in new_locations:
                        # Must deepcopy, else lists will be linked across
                        # successor configs
                        successor_config = deepcopy(config)
                        successor_config[piece] = loc
                        successors.append(successor_config)

        return successors

    def get_random_successor(self, config):
        # Cannot be the castle green; if a multi-piece type, pick one piece
        p = list(config.keys())
        p.remove("castle_green")
        chosen_piece = random.choice(p)
        successor_config = deepcopy(config)
        all_possible_locations = self.get_all_possible_locations(config)
        current_piece_locations = self.extract_piece_locations(config)

        if chosen_piece == "castle_interior":
            potential_location = random.choice(all_possible_locations)
            green_locs = self.green_locs(potential_location,
                current_piece_locations)
            while 0 == len(green_locs):
                potential_location = random.choice(all_possible_locations)
                green_locs = self.green_locs(potential_location,
                    current_piece_locations)

            green_loc_final = random.choice(green_locs)
            successor_config["castle_interior"] = potential_location
            successor_config["castle_green"] = green_loc_final

        elif chosen_piece in ["knight", "sergeant", "pikemen"]: # Multi-pieces
            new_loc = random.choice(all_possible_locations)
            index = random.choice(list(range(len(config[chosen_piece]))))
            successor_config[chosen_piece][index] = new_loc
        else: # Single pieces
            new_loc = random.choice(all_possible_locations)
            successor_config[chosen_piece] = new_loc

        return successor_config

    # TODO: ADD FUNCTIONS AS THEY ARE COMPLETED
    #       ADD WEIGHTS AS CLASS MEMBERS, FOR USE WITH GRID SEARCH
    def evaluate_config(self, config):
        return self.ways_onto_castle_green(config)

    ##########################
    ####### HEURISTICS #######
    ##########################
    # HIGHER VALUES SHOULD BE "BETTER" CONFIGURATIONS

    # DAN
    # 1. Number of ways on to the castle green (max 7)
    # NOTE: May want to count "half a way onto the green" if there is rough
    # terrain, as only mounted units would be forbidden from using this
    # approach
    def ways_onto_castle_green(self, config):
        # return should be 1 - (normalized value)
        pass

    # Artjom
    # 2. King protected/shielded by terrain (half a "point" for rough, full for
    # mountain)
    # MAX: can normalize w.r.t. forward direction and three diagonals

    # DAN
    # 3. Some measure of pieces being too close to the middle boundary,
    # especially castle and king
    # MAX: 11 (assuming 0=next to boundary)

    # DAN
    # 4. Some measure of royalty (king, prince, duke) "avengeable"
    # Could be treated as yes/no for each piece

    # Artjom
    # 5. Some measure of king, squire, archer near each other and the castle
    # MAX: Maximized by the king, squire, archer and castle each in a corner of
    # the board
    # Could be Euclidean distance?

    # Artjom
    # 6. Some measure of coverage of the enemy side of the board
    # MAX: 12 * 24 - terrain?

    # DAN
    # 7. Some measure of remainder pieces "avengeable"
    # Could be treated as yes/no for each piece

    # HOLD OFF ON THE BELOW
    # 8. Some notion of flanks being covered or board control (or both?)

    # 9. Royalty shielded by friendly pieces

    # TODO (?): Write a meta algorithm for improving the weights based on
    # subsequent game performance (could just use the greedy/random agent?)

# Based on the pseudocode provided on page 111 (and section 4.1.1, pages
# 111-114) of Russell & Norvig's "Artificial Intelligence" (4th edition)
class HillClimbing(LocalSearch):
    # Implements the basic form of the Hill Climbing algorithm
    # @param an initial configuration - if not provided a random one will be
    # chosen; having this as a parameter allows for easy reuse in a random
    # restarts context
    def get_piece_placement(self, initial=None):
        current = initial if initial is not None else self.get_random_start()
        while True:
            neighbor = self.choose_successor(current)
            if self.evaluate_config(neighbor) <= self.evaluate_config(current):
                return current
            current = neighbor

    def choose_successor(self, current_config):
        pass


class HillClimbingGreedy(HillClimbing):
    def choose_successor(self, current_config):
        successors = self.get_successor_states(current_config)
        best = successors[0]
        best_value = self.evaluate_config(best)
        for c in successors[1:]:
            value = self.evaluate_config(c)
            if value > best_value:
                best_value = value
                best = c

        return best


