import os
import argparse
from . import Emulator


parser = argparse.ArgumentParser(prog="mqe", description="Emulates .mqa execution files for Mini Quantum CPU")
parser.add_argument("input", type=str, help="executable file")
parser.add_argument("-v", "--verbose", help="be verbose", action="store_true")
args = parser.parse_args()


def pretty_time(time: int | float) -> str:
    """
    Compresses time to a smaller value (seconds to minutes to hours to days etc.)
    :param time: time in seconds
    :return: time in whatevers
    """

    # seconds to minutes
    new_time = time / 60
    if new_time < 1:
        return f"{time:.4f} seconds"
    time = new_time

    # minutes to hours
    new_time = time / 60
    if new_time < 1:
        return f"{time:.4f} minutes"
    time = new_time

    # hours to days
    new_time = time / 24
    if new_time < 1:
        return f"{time:.4f} hours"
    time = new_time

    # days to weeks
    new_time = time / 7
    if new_time < 1:
        return f"{time:.4f} days"
    time = new_time

    # weeks to months
    new_time = time / 4.345
    if new_time < 1:
        return f"{time:.4f} weeks"
    time = new_time

    # months to years (bruh)
    new_time = time / 12
    if new_time < 1:
        return f"{time:.4f} months"

    # just give up at this point
    return f"{new_time:.4f} years"


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

    # initialize the emulator
    emulator = Emulator(verbose=args.verbose)
    with open(args.input, "rb") as file:
        emulator.load_binary_file(file)

    # make a separator
    print(f"\n{'=' * 120}\n")

    # run emulation
    emulator.execute_whole()

    # print out the result
    print(f"\n\n{'=' * 120}\n")
    print(f"Finished after : {emulator.instruction_counter} instructions")
    print(f"Time in ticks  : {emulator.tick_counter} ticks")
    print(f"Time in seconds: {emulator.tick_counter * 0.025:.4f} sec")
    print(f"Compressed time: {pretty_time(emulator.tick_counter * 0.025)}")


if __name__ == '__main__':
    main()
