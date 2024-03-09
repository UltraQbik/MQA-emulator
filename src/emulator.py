import math
from .emu_types import *
from .file_system import FileManager


class Emulator:
    def __init__(self, **kwargs):
        """
        Emulator class, which does do the emulation thing.
        """

        # registers
        self.acc: int = 0                                                   # accumulator
        self.program_counter: int = 0                                       # program counter
        self.stack_pointer: int = 0                                         # stack pointer
        self.carry_flag: bool = False                                       # carry flag
        self.interrupt_register: InterruptRegister = InterruptRegister()    # interrupt register

        # page registers
        self.cache_page: int = 0                                            # cache page
        self.rom_page: int = 0                                              # ROM page

        # memory
        self.rom: bytearray = bytearray([0 for _ in range(2**16 * 2)])
        self.cache: bytearray = bytearray([0 for _ in range(2**16)])
        self.stack: bytearray = bytearray([0 for _ in range(256)])
        self.ports: bytearray = bytearray([0 for _ in range(256)])

        # interrupt extensions
        self.allow_files: bool = kwargs.get("allow_files", False)
        self.allow_sockets: bool = kwargs.get("allow_sockets", False)

        # instruction switch case
        self.instruction_set: list = [None for _ in range(128)]
        for i in range(128):
            if hasattr(self, f"_is_{i}"):
                self.instruction_set[i] = getattr(self, f"_is_{i}")
            else:
                self.instruction_set[i] = self._is__

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
        print("Instructions were loaded successfully!", end="\n\n")

    def _check_carry(self):
        self.carry_flag = self.acc > 255
        self.acc = self.acc & 255

    def _check_neg_carry(self):
        self.carry_flag = self.acc < 0
        self.acc = self.acc & 255

    def _is_acc_neg(self):
        return (self.acc & 0b1000_0000) > 0

    def _is_0(self, rom_cache_bus, data):
        # NOP
        pass

    def _is_1(self, rom_cache_bus, data):
        # LRA
        self.acc = rom_cache_bus

    def _is_2(self, rom_cache_bus, data):
        # SRA
        # address comes only from data (otherwise nothing will work)
        self.cache[data + self.cache_page * 256] = self.acc

    def _is_3(self, rom_cache_bus, data):
        # CALL
        self.stack[self.stack_pointer] = self.program_counter
        self.stack_pointer = (self.stack_pointer + 1) & 255
        self.program_counter = rom_cache_bus - 1

    def _is_4(self, rom_cache_bus, data):
        # RET
        self.stack_pointer = (self.stack_pointer - 1) & 255
        self.program_counter = self.stack[self.stack_pointer] - 1

    def _is_5(self, rom_cache_bus, data):
        # JMP
        self.program_counter = rom_cache_bus - 1

    def _is_6(self, rom_cache_bus, data):
        # JMPP
        if self.acc != 0:
            self.program_counter = rom_cache_bus - 1

    def _is_7(self, rom_cache_bus, data):
        # JMPZ
        if self.acc == 0:
            self.program_counter = rom_cache_bus - 1

    def _is_8(self, rom_cache_bus, data):
        # JMPN
        if (self.acc & 0b1000_0000) > 0:
            self.program_counter = rom_cache_bus - 1

    def _is_9(self, rom_cache_bus, data):
        # JMPC
        if self.carry_flag:
            self.program_counter = rom_cache_bus - 1

    def _is_10(self, rom_cache_bus, data):
        # CCF
        self.carry_flag = False

    def _is_11(self, rom_cache_bus, data):
        # LRP
        self.acc = self.cache[self.acc + self.cache_page]

    def _is_12(self, rom_cache_bus, data):
        # CCP
        self.cache_page = rom_cache_bus

    def _is_13(self, rom_cache_bus, data):
        # CRP
        self.rom_page = rom_cache_bus

    def _is_16(self, rom_cache_bus, data):
        # AND
        self.acc = self.acc & rom_cache_bus

    def _is_17(self, rom_cache_bus, data):
        # OR
        self.acc = self.acc | rom_cache_bus

    def _is_18(self, rom_cache_bus, data):
        # XOR
        self.acc = self.acc ^ rom_cache_bus

    def _is_19(self, rom_cache_bus, data):
        # NOT
        self.acc = 255 - self.acc

    def _is_20(self, rom_cache_bus, data):
        # LSC
        self.acc = self.acc << rom_cache_bus
        self._check_carry()

    def _is_21(self, rom_cache_bus, data):
        # RSC
        if ((self.acc >> rom_cache_bus) << rom_cache_bus) != self.acc:
            self.carry_flag = True
        self.acc = self.acc >> rom_cache_bus

    def _is_22(self, rom_cache_bus, data):
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

    def _is_23(self, rom_cache_bus, data):
        # CMPU
        if self.acc > rom_cache_bus:
            self.acc = 1
        elif self.acc == rom_cache_bus:
            self.acc = 0
        else:
            self.acc = 255

    def _is_32(self, rom_cache_bus, data):
        # ADC
        self.acc = self.acc + rom_cache_bus + self.carry_flag
        self._check_carry()

    def _is_33(self, rom_cache_bus, data):
        # SBC
        self.acc = self.acc - rom_cache_bus - self.carry_flag
        self._check_neg_carry()

    def _is_34(self, rom_cache_bus, data):
        # INC
        self.acc += 1
        self._check_carry()

    def _is_35(self, rom_cache_bus, data):
        # DEC
        self.acc -= 1
        self._check_neg_carry()

    def _is_36(self, rom_cache_bus, data):
        # ABS
        if self._is_acc_neg():
            self.acc = ((255 - self.acc) + 1) & 255

    def _is_37(self, rom_cache_bus, data):
        # MUL
        self.acc = (self.acc * rom_cache_bus) & 255

    def _is_38(self, rom_cache_bus, data):
        # DIV
        self.acc = self.acc // rom_cache_bus

    def _is_39(self, rom_cache_bus, data):
        # MOD
        self.acc = self.acc % rom_cache_bus

    def _is_40(self, rom_cache_bus, data):
        # TSE
        sin = (math.sin(self.acc / 32) + 1) / 2
        sin = int(sin * 255)
        self.acc = sin

    def _is_41(self, rom_cache_bus, data):
        # TCE
        cos = (math.cos(self.acc / 32) + 1) / 2
        cos = int(cos * 255)
        self.acc = cos

    def _is_42(self, rom_cache_bus, data):
        # ADD
        self.acc = self.acc + rom_cache_bus
        self._check_carry()

    def _is_43(self, rom_cache_bus, data):
        # SUB
        self.acc = self.acc - rom_cache_bus
        self._check_neg_carry()

    def _is_44(self, rom_cache_bus, data):
        # RPL
        if rom_cache_bus == 0:
            self.acc = 255
        else:
            self.acc = int(255 / rom_cache_bus)

    def _is_45(self, rom_cache_bus, data):
        # MULH
        self.acc = ((self.acc * rom_cache_bus) & 0b1111_1111_0000_0000) >> 8

    def _is_48(self, rom_cache_bus, data):
        # UI
        user = input("> ")
        try:
            self.acc = int(user)
        except ValueError:
            self.acc = ord(user[0])
        except IndexError:
            self.acc = 0

    def _is_49(self, rom_cache_bus, data):
        # UO
        print(self.acc)

    def _is_50(self, rom_cache_bus, data):
        # UOC
        print(chr(self.acc), end="")

    def _is_51(self, rom_cache_bus, data):
        # UOCR
        print(chr(self.acc))

    def _is_112(self, rom_cache_bus, data):
        # PRW
        self.ports[data] = self.acc

    def _is_113(self, rom_cache_bus, data):
        # PRR
        self.acc = self.ports[data]

    def _is_126(self, rom_cache_bus, data):
        # INT
        self._process_interrupt()

    def _is_127(self, rom_cache_bus, data):
        # HALT
        self.interrupt_register.is_halted = True
        raise StopIteration

    def _is__(self, rom_cache_bus, data):
        raise StopIteration

    def _process_interrupt(self):
        """
        Processes the interrupt
        """

        # FileManager - 0
        if self.allow_files and self.ports[0] == 0:
            FileManager.process(
                self,                           # emulator
                self.ports[1],                  # operation (0 - read, 1 - write)
                self.ports[2], self.ports[3],   # filepath pointer (16 bits)
                self.ports[4], self.ports[5]    # size (16 bits)
            )

        # Sockets - 1
        elif self.allow_sockets and self.ports[0] == 1:
            pass

        # nothing allowed
        else:
            # enable interrupt and die
            self.interrupt_register.interrupt = True
            raise StopIteration

    def execute_step(self):
        """
        Executes one step of the CPU
        """

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
        if memory_flag and opcode != 2:
            rom_cache_bus = self.cache[data]
        else:
            rom_cache_bus = data

        # execute instruction
        self.instruction_set[opcode](rom_cache_bus, data)

        # increment the program counter
        self.program_counter += 1

    def execute_whole(self):
        """
        Executes the entire file
        :return:
        """

        count = 0
        while True:
            try:
                self.execute_step()
            except StopIteration:
                break
            count += 1
        print(f"\n{'='*120}\nFinished after: {count} instructions")
