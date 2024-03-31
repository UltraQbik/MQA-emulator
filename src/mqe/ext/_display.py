from tkinter import Tk, Canvas, PhotoImage


"""
Simple display manager, which uses tkinter to function.
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
    ROOT: None | Tk = None
    IMAGE_BUFFER: None | PhotoImage = None

    # window width and height
    WINDOW_WIDTH: int = 128
    WINDOW_HEIGHT: int = 128

    # window update rate
    UPDATE_RATE: float = 1 / 30
    PREV_VALUE: float = 0

    @classmethod
    def initialize(cls, mode: int):
        """
        Initializes the display
        """

        # create a window
        cls.ROOT = Tk()
        if mode == 1:
            cls.ROOT.title("DisplayManager (XY mode)")
        else:
            cls.ROOT.title("DisplayManager (page mode)")

        # make canvas
        canvas = Canvas(cls.ROOT, width=cls.WINDOW_WIDTH, height=cls.WINDOW_HEIGHT, bg="#000000")
        canvas.pack(expand=True)

        # create window image buffer and put it on canvas
        cls.IMAGE_BUFFER = PhotoImage(width=cls.WINDOW_WIDTH, height=cls.WINDOW_HEIGHT)
        canvas.create_image((cls.WINDOW_WIDTH//2, cls.WINDOW_HEIGHT//2),
                            image=cls.IMAGE_BUFFER, state="normal")

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
            # width and height
            cls.WINDOW_WIDTH = emu.ports[1] & 255
            cls.WINDOW_HEIGHT = emu.ports[2] & 255

            # initialize window method
            cls.initialize(emu.ports[0])

            # set INITIALIZED to True
            cls.INITIALIZED = True

            # return
            return

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
            cls.page_update(emu.cache)

    @classmethod
    def plot(cls, x, y, val):
        # get RGB values, and put them in a range 0 - 255
        r = int((val >> 5) * 36.4285)
        g = int(((val >> 2) & 0b111) * 36.4285)
        b = int((val & 0b11) * 85)

        # plot a pixel
        cls.IMAGE_BUFFER.put(f"#{hex(r)[2:]:0>2}{hex(g)[2:]:0>2}{hex(b)[2:]:0>2}", (x, y))

    @classmethod
    def page_update(cls, cache):
        img_ptr = cls.WINDOW_WIDTH * cls.WINDOW_HEIGHT

        cls.IMAGE_BUFFER.configure(
            data=f'P5 {cls.WINDOW_WIDTH} {cls.WINDOW_HEIGHT} 255 '.encode() + cache[65536-img_ptr:]
        )
