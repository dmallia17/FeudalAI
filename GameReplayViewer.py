# Script to step through game replays for review - use "n" for the next game
# state, and "b" for back to the previous gam estate

import argparse, pickle
from pynput import keyboard

# Control globals
quit = False
display_new = False
displaying = False
index = 0
MAX_INDEX = None

def on_press(key):
    global quit, display_new, displaying, index

    if(hasattr(key,'char') and key.char == 'q'):
        return False # closes the Listener

    if(hasattr(key,'char') and key.char == 'n'):
        if not displaying and index != MAX_INDEX:
            index += 1
            display_new = True

    if(hasattr(key,'char') and key.char == 'b'):
        if not displaying and index != 0:
            index -= 1
            display_new = True



if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Review a Feudal game saved as a list of Boards")
    parser.add_argument("game_file", type=str, metavar="filename",
        help=".pkl file containing the game states")
    args = parser.parse_args()


    with open(args.game_file, "rb") as f:
        game_states = pickle.load(f)

    MAX_INDEX = len(game_states) - 1

    print("State 0")
    game_states[0].display()

    # Setup control handling
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while not quit:
        if display_new:
            displaying = True
            print("State", index)
            game_states[index].display()
            display_new = False
            displaying = False


