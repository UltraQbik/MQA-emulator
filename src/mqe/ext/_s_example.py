from . import load_extension


"""
Some sort of description about the extension
"""


class ExampleExtension:
    """
    Some kind of cool example extension
    """

    @classmethod
    def process(cls, emu):
        """
        Processes all example related interrupt calls.
        :param emu: emulator
        """

        # check interrupt operation
        if emu.ports[0] != 0:
            return

        ...

    ...


load_extension(ExampleExtension)
