# Heuristics to be used by Minimax or MCTS

import math

# Returns a normalized count of the royalty remaining for the player designated
# by color
def royalty_remaining(board, color, king_weight=1, prince_weight=2,
    duke_weight=2):
    if color == "blue":
        counts = board.blue_piece_counts
    else:
        counts = board.brown_piece_counts

    return ((king_weight * counts["king"] + prince_weight * counts["prince"] \
        + duke_weight * counts["duke"]) / \
        (3.0 * (king_weight + prince_weight + duke_weight)))

# Returns a normalized count of the other pieces remaining for the player
# designated by color
def other_remaining(board, color, knight_weight=2, sergeant_weight=1,
    pikemen_weight=1, squire_weight=1, archer_weight=1):
    if color == "blue":
        counts = board.blue_piece_counts
    else:
        counts = board.brown_piece_counts

    return (knight_weight * counts["knight"] + \
        sergeant_weight * counts["sergeant"] + \
        pikemen_weight * counts["pikemen"] + \
        squire_weight * counts["squire"] + \
        archer_weight * counts["archer"]) / \
        (10.0 * (knight_weight + sergeant_weight + pikemen_weight + \
            squire_weight + archer_weight))

def distance_to_enemy_castle(board, color):
    if color == "blue":
        pieces = board.blue_pieces
        enemy_castle_green = board.brown_castle[1]
        norm = board.max_dist_blue
    else: # brown
        pieces = board.brown_pieces
        enemy_castle_green = board.blue_castle[1]
        norm = board.max_dist_brown

    total_dist = 0
    for piece in pieces.keys():
        piece_loc = pieces[piece]
        total_dist += math.sqrt(
            ((piece_loc[0] - enemy_castle_green[0]) ** 2) + \
            ((piece_loc[1] - enemy_castle_green[1]) ** 2))

    return 1 - (total_dist / norm)


###############################################################################
###############################################################################
####################        Truncation Functions       ########################
###############################################################################
###############################################################################
def simple_piece_evaluation(board, royalty_weight=.66, other_weight=.33):
    if royalty_weight * royalty_remaining(board, "blue") + \
        other_weight * other_remaining(board, "blue") > \
        royalty_weight * royalty_remaining(board, "brown") + \
        other_weight * other_remaining(board, "brown"):
        return "blue"
    else:
        return "brown"

def piece_and_castle_evaluation(board, royalty_weight=.61, other_weight=.33,
    castle_weight=.05):
    if royalty_weight * royalty_remaining(board, "blue") + \
        other_weight * other_remaining(board, "blue") + \
        castle_weight * distance_to_enemy_castle(board, "blue") > \
        royalty_weight * royalty_remaining(board, "brown") + \
        other_weight * other_remaining(board, "brown") + \
        castle_weight * distance_to_enemy_castle(board, "brown"):
        return "blue"
    else:
        return "brown"
