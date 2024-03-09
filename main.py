import os
import time
import argparse
from src import Emulator


parser = argparse.ArgumentParser(description="Emulates .mqa execution files for Mini Quantum CPU")
parser.add_argument("input", type=str, help="executable file")
parser.add_argument("--allow-files", help="allows to read / write files",
                    action="store_true")
parser.add_argument("--allow-network", help="allows the use of sockets",
                    action="store_true")
args = parser.parse_args()


def die(message=None):
    """
    Dies with some kind of message.
    :param message: message with which the program will do the die thing
    """

    if message is not None:
        print(f"ERROR: {message}")
    exit(1)


def main():
    # file reading
    if not os.path.isfile(args.input):
        die(f"file '{args.input}' not found")
    with open(args.input, "rb") as file:
        content = file.read()

    emulator = Emulator()
    emulator.load_instructions(content)
    emulator.execute_whole()


if __name__ == '__main__':
    main()
