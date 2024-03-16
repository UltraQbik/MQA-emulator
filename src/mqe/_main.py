import os
import argparse
from . import Emulator


parser = argparse.ArgumentParser(prog="mqe", description="Emulates .mqa execution files for Mini Quantum CPU")
parser.add_argument("input", type=str, help="executable file")
parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
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

    emulator = Emulator(verbose=args.verbose)
    with open(args.input, "rb") as file:
        emulator.load_binary_file(file)
    emulator.execute_whole()


if __name__ == '__main__':
    main()
