import math
from ._emu_types import *
from ._mqis import *


class Emulator:
    def __init__(self):
        """
        Emulator class, which does do the emulation thing.
        """

        # registers
        self._acc: int = 0                                                  # accumulator
        self._program_counter: int = 0                                      # program counter
        self._acc_stack_pointer: int = 0                                    # _acc stack pointer
        self._adr_stack_pointer: int = 0                                    # stack pointer
        self._carry_flag: bool = False                                      # carry flag
        self.interrupt_register: InterruptRegister = InterruptRegister()    # interrupt register

        # page registers
        self._cache_page: int = 0                                           # cache page
        self._rom_page: int = 0                                             # ROM page

        # memory
        self._rom: bytearray = bytearray([0 for _ in range(2 ** 16 * 2)])
        self.cache: bytearray = bytearray([0 for _ in range(2**16)])
        self._acc_stack: bytearray = bytearray([0 for _ in range(256)])
        self._adr_stack: bytearray = bytearray([0 for _ in range(256)])
        self.ports: bytearray = bytearray([0 for _ in range(256)])

        # interrupt extensions
        self._includes: list = []

        # instruction counting
        self.instruction_counter = 0
        self.tick_counter = 0

        # instruction switch case
        self._instruction_set: list = [None for _ in range(128)]
        for i in range(128):
            if hasattr(self, f"_is_{i}"):
                self._instruction_set[i] = getattr(self, f"_is_{i}")
            else:
                self._instruction_set[i] = self._is__

    def load_instructions(self, instructions: bytes):
        """
        Loads the instructions into the ROM (Read-Only Memory)
        :param instructions: instructions
        """

        print("Loading the instructions...")
        for idx in range(0, len(instructions), 2):
            value_high = instructions[idx]
            value_low = instructions[idx + 1]

            self._rom[idx] = value_high
            self._rom[idx + 1] = value_low

            value = (value_high << 8) + value_low

            memory_flag = value >> 15
            data = (value >> 7) & 0b1111_1111
            opcode = value & 0b111_1111

            print("\t", memory_flag, data, opcode)
        print("Instructions were loaded successfully!", end=f"\n{'='*120}\n\n")

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
        self._program_counter = self._adr_stack[self._adr_stack_pointer] - 1

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
            include.process(self)

    def execute_step(self):
        """
        Executes one step of the CPU
        """

        # fetch the instruction bytes
        value_high = self._rom[self._program_counter * 2]
        value_low = self._rom[self._program_counter * 2 + 1]

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

        # add to time
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

        while True:
            try:
                self.execute_step()
            except StopIteration:
                break
            self.instruction_counter += 1
        print(f"\n\n{'='*120}\nFinished after: {self.instruction_counter} instructions;")
        print(f"Time in ticks: {self.tick_counter} ticks;")
        print(f"Time in seconds: {self.tick_counter * 0.025:.4f} sec.")
