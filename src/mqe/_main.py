import os
import argparse
from . import Emulator


parser = argparse.ArgumentParser(prog="mqe", description="Emulates .mqa execution files for Mini Quantum CPU")
parser.add_argument("input", type=str, help="executable file")
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
