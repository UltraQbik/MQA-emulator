import os


"""
Be 10x more careful when using this.
If you will accidentally rewrite and mess up you system files or drivers, it is your fault.
"""


class EmulatorStub:
    interrupt_register = None
    cache: bytearray
    ports: bytearray


class FileManager:
    """
    The file manager class, uses interrupt operation 0.
    """

    @classmethod
    def process(cls, emu: EmulatorStub):
        """
        Processes all file related interrupt calls
        :param emu: emulator
        """

        # check interrupt operations
        if emu.ports[0] != 0:
            return

        # operation - port 1
        # ptr_low, ptr_high - 2, 3
        # size_low, size_high - 4, 5

        operation = emu.ports[1]
        ptr = int.from_bytes(emu.ports[2:4], 'little')
        size = int.from_bytes(emu.ports[4:6], 'little')

        if operation == 0:
            cls.read_file(emu, ptr, size)
        else:
            cls.write_file(emu, ptr, size)

    @staticmethod
    def read_file(emu, ptr: int, size: int):
        """
        Reads the file, and writes its bytes into cache. If any error occurs, it will simply die
        :param emu: emulator
        :param ptr: where the file data will be written
        :param size: size
        """

        # path is a null terminated string in cache
        path = ""
        pointer = 0
        while emu.cache[pointer] != 0:
            path += chr(emu.cache[pointer])
            pointer += 1

        # check if the filepath is valid
        if not os.path.isfile(path):
            return

        # if no size is given, just assume it's all of it
        if size == 0:
            size = -1

        # read the file (character by character)
        with open(path, "rb") as file:
            offset = 0
            while offset != size:
                # check if the pointer exceeds cache
                if ptr + offset > 65535:
                    return

                # fetch a character
                value = file.read(1)
                if not value:
                    return

                # write into cache
                emu.cache[ptr + offset] = value[0]
                offset += 1

    @staticmethod
    def write_file(emu, ptr: int, size: int):
        """
        Writes to a file. If any error occurs, it will simply die.
        :param emu: emulator
        :param ptr: pointer to filepath
        :param size: size of the file (in bytes)
        :return:
        """

        # path is a null terminated string in cache
        path = ""
        pointer = 0
        while emu.cache[pointer] != 0:
            path += chr(emu.cache[pointer])
            pointer += 1

        # write the file!
        with open(path, "wb") as file:
            for i in range(size):
                # check if the pointer exceeds cache
                if ptr + i > 65535:
                    return

                # write into file
                file.write(bytes([emu.cache[ptr + i]]))
