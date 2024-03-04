class Emulator:
    def __init__(self):
        """
        Emulator class, which does do the emulation thing.
        """

        # registers
        self.ACC: int = 0
        self.PC: int = 0
        self.SP: int = 0
        self.IR: int = 0

        # memory
        self.rom: bytearray = bytearray([0 for _ in range(2**16)])
        self.cache: bytearray = bytearray([0 for _ in range(2**16)])
        self.ports: bytearray = bytearray([0 for _ in range(256)])

    def load_instructions(self, instructions: bytes):
        """
        Loads the instructions into the ROM (Read-Only Memory)
        :param instructions: instructions
        """

        for idx in range(0, len(instructions), 2):
            value_high = instructions[idx]
            value_low = instructions[idx + 1]

            self.rom[idx] = value_high
            self.rom[idx + 1] = value_low

            value = (value_high << 8) + value_low

            memory_flag = value >> 15
            data = (value >> 7) & 0b1111_1111
            opcode = value & 0b111_1111

            print(memory_flag, data, opcode)
