"""
Simplistic terminal only extension for MQE.
Once included, only image data can be displayed on the terminal.
"""


class DisplayManager:
    @classmethod
    def process(cls, emu):
        """
        Processes all display related interrupt calls
        :param emu: emulator
        """

        # check interrupt operations
        if emu.ports[0] != 1 or emu.ports[0] != 2:
            return
