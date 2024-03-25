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

    # display manager parameters
    INITIALIZED: bool = False

    # window variables
    ROOT = None
    IMAGE_BUFFER = None

    # window width and height
    WINDOW_WIDTH = 128
    WINDOW_HEIGHT = 128

    @classmethod
    def initialize(cls, mode: int):
        """
        Initializes the display
        """

        # initialize Tk
        from tkinter import Tk, Canvas, PhotoImage, mainloop

        # create a window
        cls.ROOT = Tk()
        if mode == 1:
            cls.ROOT.title("DisplayManager (XY mode)")
        else:
            cls.ROOT.title("DisplayManager (page mode)")

        # make canvas
        canvas = Canvas(cls.ROOT, width=cls.WINDOW_WIDTH, height=cls.WINDOW_HEIGHT, bg="#000000")
        canvas.pack()

        # create window image buffer and put it on canvas
        cls.IMAGE_BUFFER = PhotoImage(width=cls.WINDOW_WIDTH, height=cls.WINDOW_HEIGHT)
        canvas.create_image((cls.WINDOW_WIDTH//2, cls.WINDOW_HEIGHT//2), image=cls.IMAGE_BUFFER, state="normal")

        # start the window
        mainloop()

    @classmethod
    def process(cls, emu):
        """
        Processes all display related interrupt calls
        :param emu: emulator
        """

        # check interrupt operations
        if emu.ports[0] != 1 and emu.ports[0] != 2:
            return

        # check initialization
        if not cls.INITIALIZED:
            cls.initialize(emu.ports[0])

            # set INITIALIZED to True
            cls.INITIALIZED = True

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
