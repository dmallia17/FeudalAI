# Heuristics to be used by Minimax or MCTS

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




