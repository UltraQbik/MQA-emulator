class InstructionSet:
    instruction_set = {
        0:      {"name": "NOP",     "ROM": 13,  "cache": 13},
        1:      {"name": "LRA",     "ROM": 13,  "cache": 13},
        2:      {"name": "SRA",     "ROM": 13,  "cache": 13},
        3:      {"name": "CALL",    "ROM": 13,  "cache": 13},   # assume 13 ticks
        4:      {"name": "RET",     "ROM": 13,  "cache": 13},   # assume 13 ticks
        5:      {"name": "JMP",     "ROM": 13,  "cache": 13},
        6:      {"name": "JMPP",    "ROM": 13,  "cache": 13},
        7:      {"name": "JMPZ",    "ROM": 13,  "cache": 13},
        8:      {"name": "JMPN",    "ROM": 13,  "cache": 13},
        9:      {"name": "JMPC",    "ROM": 13,  "cache": 13},
        10:     {"name": "CCF",     "ROM": 13,  "cache": 13},
        11:     {"name": "LRP",     "ROM": 13,  "cache": 13},
        12:     {"name": "CCP",     "ROM": 13,  "cache": 13},
        13:     {"name": "CRP",     "ROM": 13,  "cache": 13},
        14:     {"name": "PUSH",    "ROM": 13,  "cache": 13},   # assume 13 ticks
        15:     {"name": "POP",     "ROM": 13,  "cache": 13},   # assume 13 ticks
        16:     {"name": "AND",     "ROM": 13,  "cache": 13},
        17:     {"name": "OR",      "ROM": 13,  "cache": 13},
        18:     {"name": "XOR",     "ROM": 13,  "cache": 13},
        19:     {"name": "NOT",     "ROM": 13,  "cache": 13},
        20:     {"name": "LSC",     "ROM": 13,  "cache": 13},
        21:     {"name": "RSC",     "ROM": 13,  "cache": 13},
        22:     {"name": "CMP",     "ROM": 13,  "cache": 13},   # assume 13 ticks
        23:     {"name": "CMPU",    "ROM": 13,  "cache": 13},   # assume 13 ticks
        32:     {"name": "ADC",     "ROM": 13,  "cache": 17},
        33:     {"name": "SBC",     "ROM": 14,  "cache": 18},
        34:     {"name": "INC",     "ROM": 13,  "cache": 13},
        35:     {"name": "DEC",     "ROM": 13,  "cache": 13},
        36:     {"name": "ABS",     "ROM": 13,  "cache": 13},
        37:     {"name": "MUL",     "ROM": 19,  "cache": 23},
        38:     {"name": "DIV",     "ROM": 44,  "cache": 49},
        39:     {"name": "MOD",     "ROM": 49,  "cache": 55},
        40:     {"name": "TSE",     "ROM": 13,  "cache": 13},   # LUT is probably 13 ticks
        41:     {"name": "TCE",     "ROM": 13,  "cache": 13},   # LUT 13 ticks
        42:     {"name": "ADD",     "ROM": 13,  "cache": 17},
        43:     {"name": "SUB",     "ROM": 14,  "cache": 18},
        44:     {"name": "RPL",     "ROM": 13,  "cache": 13},   # LUT 13 ticks
        45:     {"name": "MULH",    "ROM": 19,  "cache": 23},   # assume same timings as in MUL
        48:     {"name": "UI",      "ROM": 13,   "cache": 13},  # deprecated
        49:     {"name": "UO",      "ROM": 13,   "cache": 13},  # deprecated
        50:     {"name": "UOC",     "ROM": 13,   "cache": 13},  # deprecated
        51:     {"name": "UOCR",    "ROM": 13,   "cache": 13},  # deprecated
        112:    {"name": "PRW",     "ROM": 13,  "cache": 13},
        113:    {"name": "PRR",     "ROM": 13,  "cache": 13},
        126:    {"name": "INT",     "ROM": 0,   "cache": 0},    # don't really have a time, as they halt
        127:    {"name": "HALT",    "ROM": 0,   "cache": 0}     # same here
    }
