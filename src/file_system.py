import os


"""
Be 10x more careful when using this.
If you will accidentally rewrite and mess up you system files or drivers, it is your fault.
"""


class FileManager:
    @classmethod
    def process(cls, emu, operation: int, ptr_low: int, ptr_high: int, size_low: int, size_high: int):
        """
        Processes all file related interrupt calls
        :param emu: emulator
        :param operation: operation (0 - read, 1 - write)
        :param ptr_low: lower part of the 16 bit pointer
        :param ptr_high: higher part of the 16 bit pointer
        :param size_low: lower part of the 16 bit length of the file (in bytes)
        :param size_high: higher part of the 16 bit length of the file (in bytes)
        """

        ptr = (ptr_high << 8) + ptr_low
        size = (size_high << 8) + size_low

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
                emu.cache[ptr + offset] = int(value)
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
                file.write(bytes(emu.cache[ptr + i]))
