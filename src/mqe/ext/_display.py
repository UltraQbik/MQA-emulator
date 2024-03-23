import os


"""
Simplistic terminal only extension for MQE.
Once included, only image data can be displayed on the terminal.
"""


class DisplayManager:
    """
    The display manager class, uses interrupt operations 1 and 2.
    1 for xy mode
    2 for page mode
    """

    INITIATED: bool = False

    @classmethod
    def process(cls, emu):
        """
        Processes all display related interrupt calls
        :param emu: emulator
        """

        # check interrupt operations
        if emu.ports[0] != 1 and emu.ports[0] != 2:
            return

        if not cls.INITIATED:
            os.system("")
            print("\n".join([' ' * 120 for _ in range(30)]))
            cls.INITIATED = True

        # XY mode
        if emu.ports[0] == 1:
            # x - port 1
            # y - port 2
            # val - port 3

            x = emu.ports[1]
            y = emu.ports[2]
            val = emu.ports[3]

            cls.plot(x, y, val)

        # page mode
        elif emu.ports[0] == 2:
            pass

    @staticmethod
    def plot(x, y, val):
        print(f"\033[{y};{x}H", end=chr(val), flush=True)
