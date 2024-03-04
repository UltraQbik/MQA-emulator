class Emulator:
    def __init__(self):
        """
        Emulator class, which does do the emulation thing.
        """

        # registers
        self.acc: int = 0                                                   # accumulator
        self.program_counter: int = 0                                       # program counter
        self.stack_pointer: int = 0                                         # stack pointer
        self.interrupt_register: list[bool] = [False, False, False, False]  # interrupt register
        self.carry_flag: bool = False                                       # carry flag

        # page registers
        self.cache_page: int = 0                                            # cache page
        self.rom_page: int = 0                                              # ROM page

        # memory
        self.rom: bytearray = bytearray([0 for _ in range(2**16 * 2)])
        self.cache: bytearray = bytearray([0 for _ in range(2**16)])
        self.ports: bytearray = bytearray([0 for _ in range(256)])

    def load_instructions(self, instructions: bytes):
        """
        Loads the instructions into the ROM (Read-Only Memory)
        :param instructions: instructions
        """

        print("Loading the instructions...")
        for idx in range(0, len(instructions), 2):
            value_high = instructions[idx]
            value_low = instructions[idx + 1]

            self.rom[idx] = value_high
            self.rom[idx + 1] = value_low

            value = (value_high << 8) + value_low

            memory_flag = value >> 15
            data = (value >> 7) & 0b1111_1111
            opcode = value & 0b111_1111

            print("\t", memory_flag, data, opcode)
        print("Instructions are loaded successfully!", end="\n\n")

    def _check_carry(self):
        if self.acc > 255:
            self.carry_flag = True
        self.acc = self.acc % 256

    def _check_neg_carry(self):
        if self.acc < 0:
            self.carry_flag = True
        self.acc = self.acc % 256

    def _is_acc_neg(self):
        return (self.acc & 0b1000_0000) > 0

    def _set_interrupt_register(self,
                                is_halted: bool = False,
                                interrupt: bool = False,
                                wrong: bool = False):
        # 5 bit register
        # 1 | 2 | 3 | 4 | 5
        # 1 - is_halted
        # 2 - interrupt
        # 3 - wrong (instruction)
        # 4, 5 - reserved

        self.interrupt_register[0] = is_halted
        self.interrupt_register[1] = interrupt
        self.interrupt_register[2] = wrong

    def execute_step(self):
        """
        Executes one step of the CPU
        """

        # if any of the interrupts are enabled
        if any(self.interrupt_register):
            return

        # fetch the instruction bytes
        value_high = self.rom[self.program_counter * 2]
        value_low = self.rom[self.program_counter * 2 + 1]

        # combine the instruction
        value = (value_high << 8) + value_low

        # decode the instruction
        memory_flag = value >> 15
        data = (value >> 7) & 0b1111_1111
        opcode = value & 0b111_1111

        # if the memory flag is on, then the value is taken from cache
        if memory_flag:
            rom_cache_bus = self.cache[data]
        else:
            rom_cache_bus = data

        # execute instruction
        match opcode:
            case 0:
                # NOP
                pass
            case 1:
                # LRA
                self.acc = rom_cache_bus
            case 2:
                # SRA
                # address comes only from data (otherwise nothing will work)
                self.cache[data + self.cache_page * 256] = self.acc
            case 3:
                # CALL
                # TODO: make subroutine calls
                pass
            case 4:
                # RET
                # TODO: make subroutine returns
                pass
            case 5:
                # JMP
                self.program_counter = rom_cache_bus
                self.program_counter -= 1
            case 6:
                # JMPP
                if self.acc != 0:
                    self.program_counter = rom_cache_bus
                    self.program_counter -= 1
            case 7:
                # JMPZ
                if self.acc == 0:
                    self.program_counter = rom_cache_bus
                    self.program_counter -= 1
            case 8:
                # JMPN
                if (self.acc & 0b1000_0000) > 0:
                    self.program_counter = rom_cache_bus
                    self.program_counter -= 1
            case 9:
                # JMPC
                if self.carry_flag:
                    self.program_counter = rom_cache_bus
                    self.program_counter -= 1
            case 10:
                # CCF
                self.carry_flag = False
            case 11:
                # LRP
                self.acc = self.cache[self.acc + self.cache_page]
            case 12:
                # CCP
                self.cache_page = rom_cache_bus
            case 13:
                # CRP
                self.rom_page = rom_cache_bus

            case 16:
                # AND
                self.acc = self.acc & rom_cache_bus
            case 17:
                # OR
                self.acc = self.acc | rom_cache_bus
            case 18:
                # XOR
                self.acc = self.acc ^ rom_cache_bus
            case 19:
                # NOT
                self.acc = 255 - self.acc
            case 20:
                # LSC
                self.acc = self.acc << rom_cache_bus
                self._check_carry()
            case 21:
                # RSC
                self.acc = self.acc >> rom_cache_bus
                # TODO: make carry flag work
            case 22:
                # CMP
                negative = (self.acc & 0b1000_0000) ^ (rom_cache_bus & 0b1000_0000)
                if self.acc > rom_cache_bus:
                    self.acc = 1
                elif self.acc == rom_cache_bus:
                    self.acc = 0
                else:
                    self.acc = 255
                if negative:
                    self.acc = 255 - self.acc
            case 23:
                # CMPU
                if self.acc > rom_cache_bus:
                    self.acc = 1
                elif self.acc == rom_cache_bus:
                    self.acc = 0
                else:
                    self.acc = 255

            case 32:
                # ADC
                self.acc = self.acc + rom_cache_bus + self.carry_flag
                self._check_carry()
            case 33:
                # SBC
                self.acc = self.acc - rom_cache_bus + self.carry_flag
                self._check_neg_carry()
            case 34:
                # INC
                self.acc += 1
                self._check_carry()
            case 35:
                # DEC
                self.acc -= 1
                self._check_neg_carry()
            case 36:
                # ABS
                if self._is_acc_neg():
                    self.acc = ((255 - self.acc) + 1) % 256
            case 37:
                # MUL
                self.acc = self.acc * rom_cache_bus
                if self.acc > 255:
                    self.acc = self.acc % 256
            case 38:
                # DIV
                self.acc = self.acc // rom_cache_bus
            case 39:
                # MOD
                self.acc = self.acc % rom_cache_bus
            case 40:
                # TSE
                # TODO: make sin
                pass
            case 41:
                # TCE
                # TODO: make cos
                pass
            case 42:
                # ADD
                self.acc = self.acc + rom_cache_bus
                self._check_carry()
            case 43:
                # SUB
                self.acc = self.acc - rom_cache_bus
                self._check_neg_carry()
            case 44:
                # RPL
                # TODO: make reciprocals
                pass
            case 45:
                # MULH
                # TODO: make multiplication high
                pass

            case 48:
                # UI
                # TODO: make user input
                pass
            case 49:
                # UO
                print(self.acc)
            case 50:
                # UOC
                print(chr(self.acc), end="")
            case 51:
                # UOCR
                print(chr(self.acc))

            case 112:
                # PRW
                self.ports[data] = self.acc
            case 113:
                # PRR
                self.acc = self.ports[data]

            case 126:
                # INT
                self._set_interrupt_register(interrupt=True)
            case 127:
                # HALT
                self._set_interrupt_register(is_halted=True)
                return

            case _:
                self._set_interrupt_register(wrong=True)
                return

        # increment the program counter
        # note: inside the jump instructions there are '-= 1' things
        # they exist to jump to the right place
        self.program_counter += 1

        # safety check
        self.acc = self.acc % 256

    def execute_whole(self):
        """
        Executes the entire file
        :return:
        """

        while not any(self.interrupt_register):
            self.execute_step()
