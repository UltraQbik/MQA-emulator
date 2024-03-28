import math
from types import ModuleType
from typing import BinaryIO
from ._emu_types import *
from ._mqis import *
from .ext import *


def pretty_time(time: int | float) -> str:
    """
    Compresses time to a smaller value (seconds to minutes to hours to days etc.)
    :param time: time in seconds
    :return: time in whatevers
    """

    # seconds to minutes
    new_time = time / 60
    if new_time < 1:
        return f"{time:.4f} seconds"
    time = new_time

    # minutes to hours
    new_time = time / 60
    if new_time < 1:
        return f"{time:.4f} minutes"
    time = new_time

    # hours to days
    new_time = time / 24
    if new_time < 1:
        return f"{time:.4f} hours"
    time = new_time

    # days to weeks
    new_time = time / 7
    if new_time < 1:
        return f"{time:.4f} days"
    time = new_time

    # weeks to months
    new_time = time / 4.345
    if new_time < 1:
        return f"{time:.4f} weeks"
    time = new_time

    # months to years (bruh)
    new_time = time / 12
    if new_time < 1:
        return f"{time:.4f} months"

    # just give up at this point
    return f"{new_time:.4f} years"


class Emulator:
    INCLUDED_LIBS: dict[str, ModuleType] = {
        "FileManager": FileManager,
        "DisplayManager": DisplayManager,
    }

    def __init__(self, **kwargs):
        """
        Emulator class, which does do the emulation thing.
        """

        # registers
        self._acc: int = 0                                                  # accumulator
        self._bacc: int = 0                                                 # baccumulator
        self._program_counter: int = 0                                      # program counter
        self._acc_stack_pointer: int = 0                                    # _acc stack pointer
        self._adr_stack_pointer: int = 0                                    # stack pointer
        self._carry_flag: bool = False                                      # carry flag
        self.interrupt_register: InterruptRegister = InterruptRegister()    # interrupt register

        # page registers
        self._cache_page: int = 0                                           # cache page
        self._rom_page: int = 0                                             # ROM page

        # memory
        self._rom: bytearray = bytearray()
        self.cache: bytearray = bytearray([0 for _ in range(2**16)])
        self._acc_stack: bytearray = bytearray([0 for _ in range(256)])
        self._adr_stack: bytearray = bytearray([0 for _ in range(256)])
        self.ports: bytearray = bytearray([0 for _ in range(256)])

        # emulator specific
        self._verbose: bool = kwargs.get("verbose", False)
        self._cpu_version: str = "1.1"
        self._includes: list[str] = []

        # instruction counting
        self.instruction_counter = 1
        self.tick_counter = 0

        # instruction switch case
        self._instruction_set: list = [None for _ in range(128)]
        for i in range(128):
            if hasattr(self, f"_is_{i}"):
                self._instruction_set[i] = getattr(self, f"_is_{i}")
            else:
                self._instruction_set[i] = self._is__

    def print(self, *values, sep: str | None = " ", end: str | None = "\n", flush: bool = False):
        if self._verbose:
            print(*values, sep=sep, end=end, flush=flush)

    def load_binary_file(self, file: BinaryIO):
        """
        Loads the binary executable into the ROM (Read-Only Memory)
        :param file: binary file
        """

        #               |                    : 10 bytes total
        #               | cpuVersion         : 4  bytes - "1.1 "
        # little_endian | includeSectionSize : 2  bytes - amount of bytes in include section
        # little_endian | assemblySectionSize: 4  bytes - amount of bytes in code
        # little_endian | includeSectionData : N  bytes - the include data
        # little_endian | assemblySectionData: N  bytes - the code data

        cpu_version = file.read(4).decode('ASCII', 'replace')
        include_section_size = int.from_bytes(file.read(2), 'little')
        assembly_section_size = int.from_bytes(file.read(4), 'little')
        self.print("Header data:")
        self.print(f"\tcpuVersion:          {cpu_version}")
        self.print(f"\tincludeSectionSize:  {include_section_size}")
        self.print(f"\tassemblySectionSize: {assembly_section_size}")
        self.print("Header end.")

        if include_section_size > 0:
            self.print("Include section start:")
            include_section_data = bytearray()
            for _ in range(include_section_size):
                # fetch character
                char = file.read(1)

                # check EOF
                if not char:
                    print("\nERROR: file ended before the include section could be read fully")
                    exit(1)

                # if character is a newline, then it's a new include
                if char == b'\n':
                    try:
                        decoded_include = include_section_data.decode('ASCII')
                    except UnicodeDecodeError:
                        print("\nERROR: unable to decode include name")
                        exit(1)

                    self._includes.append(decoded_include)
                    self.print(f"\t> {decoded_include}")
                    include_section_data.clear()

                # otherwise append a character to the include section
                else:
                    include_section_data += char
            self.print("Include section end.")

        self.print("Assembly section start:")
        for idx in range(0, assembly_section_size & 0b1_1111_1111_1111_1111, 2):
            # fetch bytes
            val_low = file.read(1)
            val_high = file.read(1)

            # check EOF
            if not val_low or not val_high:
                print("ERROR: file ended before the assembly section could be read fully")
                exit(1)

            # verbose print
            if self._verbose:
                value = (int.from_bytes(val_high) << 8) + int.from_bytes(val_low)

                # instruction mnemonic
                mnemonic = InstructionSet.instruction_set.get(value & 127)["name"]

                # if memory flag is on
                if value >> 15:
                    print(f"\t{mnemonic: <4} ${(value >> 7) & 255}")
                else:
                    print(f"\t{mnemonic: <4} {(value >> 7) & 255}")

            # write to rom
            self._rom += val_low
            self._rom += val_high
        self.print(f"Assembly section end.")

        # check versions
        if float(self._cpu_version) < float(cpu_version.strip()):
            print("WARN: the executable file is for newer MQ version; some things may not work")

    def _check_carry(self):
        self._carry_flag = self._acc > 255
        self._acc = self._acc & 255

    def _check_neg_carry(self):
        self._carry_flag = self._acc < 0
        self._acc = self._acc & 255

    def _is_acc_neg(self):
        return (self._acc & 0b1000_0000) > 0

    def _is_0(self, rom_cache_bus):
        # NOP
        pass

    def _is_1(self, rom_cache_bus):
        # LRA
        self._acc = rom_cache_bus

    def _is_2(self, rom_cache_bus):
        # SRA
        # rom_cache_bus will equal to DATA from ROM, no cache used
        self.cache[(self._cache_page << 8) + rom_cache_bus] = self._acc

    def _is_3(self, rom_cache_bus):
        # CALL
        self._adr_stack[self._adr_stack_pointer] = self._program_counter
        self._adr_stack_pointer = (self._adr_stack_pointer + 1) & 255
        self._program_counter = (self._rom_page << 8) + (rom_cache_bus - 1)

    def _is_4(self, rom_cache_bus):
        # RET
        self._adr_stack_pointer = (self._adr_stack_pointer - 1) & 255
        self._program_counter = self._adr_stack[self._adr_stack_pointer]
        self._acc = rom_cache_bus

    def _is_5(self, rom_cache_bus):
        # JMP
        self._program_counter = (self._rom_page << 8) + (rom_cache_bus - 1)

    def _is_6(self, rom_cache_bus):
        # JMPP
        if self._acc != 0:
            self._program_counter = (self._rom_page << 8) + (rom_cache_bus - 1)

    def _is_7(self, rom_cache_bus):
        # JMPZ
        if self._acc == 0:
            self._program_counter = (self._rom_page << 8) + (rom_cache_bus - 1)

    def _is_8(self, rom_cache_bus):
        # JMPN
        if (self._acc & 0b1000_0000) > 0:
            self._program_counter = (self._rom_page << 8) + (rom_cache_bus - 1)

    def _is_9(self, rom_cache_bus):
        # JMPC
        if self._carry_flag:
            self._program_counter = (self._rom_page << 8) + (rom_cache_bus - 1)

    def _is_10(self, rom_cache_bus):
        # CCF
        self._carry_flag = False

    def _is_11(self, rom_cache_bus):
        # LRP
        self._acc = self.cache[(self._cache_page << 8) + self._acc]

    def _is_12(self, rom_cache_bus):
        # CCP
        self._cache_page = rom_cache_bus

    def _is_13(self, rom_cache_bus):
        # CRP
        self._rom_page = rom_cache_bus

    def _is_14(self, rom_cache_bus):
        # PUSH
        self._acc_stack[self._acc_stack_pointer] = self._acc
        self._acc_stack_pointer = (self._acc_stack_pointer + 1) & 255

    def _is_15(self, rom_cache_bus):
        # POP
        self._acc_stack_pointer = (self._acc_stack_pointer - 1) & 255
        self._acc = self._acc_stack[self._acc_stack_pointer]

    def _is_16(self, rom_cache_bus):
        # AND
        self._acc = self._acc & rom_cache_bus

    def _is_17(self, rom_cache_bus):
        # OR
        self._acc = self._acc | rom_cache_bus

    def _is_18(self, rom_cache_bus):
        # XOR
        self._acc = self._acc ^ rom_cache_bus

    def _is_19(self, rom_cache_bus):
        # NOT
        self._acc = 255 - self._acc

    def _is_20(self, rom_cache_bus):
        # LSC
        self._acc = (self._acc << rom_cache_bus) + self._carry_flag
        self._check_carry()

    def _is_21(self, rom_cache_bus):
        # RSC
        temp_acc = self._acc
        self._acc = (self._acc >> rom_cache_bus) + (self._carry_flag << 7)
        if ((temp_acc >> rom_cache_bus) << rom_cache_bus) != temp_acc:
            self._carry_flag = True

    def _is_22(self, rom_cache_bus):
        # CMP
        negative = (self._acc & 0b1000_0000) ^ (rom_cache_bus & 0b1000_0000)
        if self._acc > rom_cache_bus:
            self._acc = 1
        elif self._acc == rom_cache_bus:
            self._acc = 0
        else:
            self._acc = 255
        if negative:
            self._acc = 255 - self._acc

    def _is_23(self, rom_cache_bus):
        # CMPU
        if self._acc > rom_cache_bus:
            self._acc = 1
        elif self._acc == rom_cache_bus:
            self._acc = 0
        else:
            self._acc = 255

    def _is_32(self, rom_cache_bus):
        # ADC
        self._acc = self._acc + rom_cache_bus + self._carry_flag
        self._check_carry()

    def _is_33(self, rom_cache_bus):
        # SBC
        self._acc = self._acc - rom_cache_bus - self._carry_flag
        self._check_neg_carry()

    def _is_34(self, rom_cache_bus):
        # INC
        self._acc += 1
        self._check_carry()

    def _is_35(self, rom_cache_bus):
        # DEC
        self._acc -= 1
        self._check_neg_carry()

    def _is_36(self, rom_cache_bus):
        # ABS
        if self._is_acc_neg():
            self._acc = ((255 - self._acc) + 1) & 255

    def _is_37(self, rom_cache_bus):
        # MUL
        self._acc = (self._acc * rom_cache_bus) & 255

    def _is_38(self, rom_cache_bus):
        # DIV
        self._acc = self._acc // rom_cache_bus

    def _is_39(self, rom_cache_bus):
        # MOD
        self._acc = self._acc % rom_cache_bus

    def _is_40(self, rom_cache_bus):
        # TSE
        sin = (math.sin(self._acc / 32) + 1) / 2
        sin = int(sin * 255)
        self._acc = sin

    def _is_41(self, rom_cache_bus):
        # TCE
        cos = (math.cos(self._acc / 32) + 1) / 2
        cos = int(cos * 255)
        self._acc = cos

    def _is_42(self, rom_cache_bus):
        # ADD
        self._acc = self._acc + rom_cache_bus
        self._check_carry()

    def _is_43(self, rom_cache_bus):
        # SUB
        self._acc = self._acc - rom_cache_bus
        self._check_neg_carry()

    def _is_44(self, rom_cache_bus):
        # RPL
        if rom_cache_bus == 0:
            self._acc = 255
        else:
            self._acc = int(255 / rom_cache_bus)

    def _is_45(self, rom_cache_bus):
        # MULH
        self._acc = ((self._acc * rom_cache_bus) & 0b1111_1111_0000_0000) >> 8

    def _is_48(self, rom_cache_bus):
        # UI
        user = input("> ")
        try:
            self._acc = int(user)
        except ValueError:
            self._acc = ord(user[0])
        except IndexError:
            self._acc = 0

    def _is_49(self, rom_cache_bus):
        # UO
        print(self._acc)

    def _is_50(self, rom_cache_bus):
        # UOC
        print(chr(self._acc), end="")

    def _is_51(self, rom_cache_bus):
        # UOCR
        print(chr(self._acc))

    def _is_52(self, rom_cache_bus):
        # LRB
        self._bacc = rom_cache_bus

    def _is_53(self, rom_cache_bus):
        # SRP
        self.cache[(self._cache_page << 8) + self._bacc] = self._acc

    def _is_54(self, rom_cache_bus):
        # TAB
        self._bacc = self._acc

    def _is_112(self, rom_cache_bus):
        # PRW
        self.ports[rom_cache_bus] = self._acc

    def _is_113(self, rom_cache_bus):
        # PRR
        self._acc = self.ports[rom_cache_bus]

    def _is_126(self, rom_cache_bus):
        # INT
        self._process_interrupt()

    def _is_127(self, rom_cache_bus):
        # HALT
        self.interrupt_register.is_halted = True
        raise StopIteration

    def _is__(self, rom_cache_bus):
        raise StopIteration

    def _process_interrupt(self):
        """
        Processes the interrupt
        """

        # if there are no includes, then just die
        if len(self._includes) == 0:
            self.interrupt_register.interrupt = True
            raise StopIteration

        # process all the included libs
        for include in self._includes:
            if include not in self.INCLUDED_LIBS:
                self.print(f"WARN: incorrect include '{include}'")

            self.INCLUDED_LIBS[include].process(self)

    def execute_step(self):
        """
        Executes one step of the CPU
        """

        # fetch the instruction bytes
        value_low = self._rom[self._program_counter * 2]
        value_high = self._rom[self._program_counter * 2 + 1]

        # combine the instruction
        value = (value_high << 8) + value_low

        # decode the instruction
        memory_flag = value >> 15
        data = (value >> 7) & 0b1111_1111
        opcode = value & 0b111_1111

        # if the memory flag is on, then the value is taken from cache
        if memory_flag and opcode != 2:
            rom_cache_bus = self.cache[(self._cache_page << 8) + data]
        else:
            rom_cache_bus = data

        # execute instruction
        self._instruction_set[opcode](rom_cache_bus)

        # display manager
        if DisplayManager.ROOT is not None:
            DisplayManager.ROOT.update()

        # add to time
        self.instruction_counter += 1
        if memory_flag:
            self.tick_counter += InstructionSet.instruction_set[opcode]["cache"]
        else:
            self.tick_counter += InstructionSet.instruction_set[opcode]["ROM"]

        # increment the program counter
        self._program_counter += 1

    def execute_whole(self):
        """
        Executes the entire file
        :return:
        """

        print(f"\n{'='*120}\n")
        while True:
            try:
                self.execute_step()
            except StopIteration:
                break
            except IndexError:
                print("WARN: program counter overflow; halted")
                break
            except KeyboardInterrupt:
                break
        print(f"\n\n{'='*120}\n")
        print(f"Finished after : {self.instruction_counter} instructions")
        print(f"Time in ticks  : {self.tick_counter} ticks")
        print(f"Time in seconds: {self.tick_counter * 0.025:.4f} sec")
        print(f"Compressed time: {pretty_time(self.tick_counter * 0.025)}")
