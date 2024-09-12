from instruction_data import (
    GLOBAL_INSTRUCTIONS_MAP,
    GLOBAL_REGISTER_NAMES,
    InstructionInfo,
    Encodings,
)
from byte_utils import parse_modrm, parse_sib, get_file


# simple data class for building up a disassembled instruction with string tokens
class Instruction:
    def __init__(
        self,
        mnemonic=None,
        encoding=None,
        immediate=None,
        reg=None,
        rm=None,
        scale=None,
        index=None,
        base=None,
        is_db=False,
    ):
        self.mnemonic = mnemonic
        self.encoding = encoding
        self.immediate = immediate
        self.reg = reg
        self.rm = rm
        self.scale = scale
        self.index = index
        self.base = base
        self.is_db = is_db

    def __str__(self) -> str:

        # handle db
        if self.is_db:
            return f"db {self.immediate}"

        # print instructions based on encoding
        if self.encoding == Encodings.M:
            return f"{self.mnemonic} {self.rm}"
        elif self.encoding == Encodings.MI:
            return f"{self.mnemonic} {self.rm}, {self.immediate}"
        elif self.encoding == Encodings.MR:
            return f"{self.mnemonic} {self.rm}, {self.reg}"
        elif self.encoding == Encodings.RM:
            return f"{self.mnemonic} {self.reg}, {self.rm}"
        elif self.encoding == Encodings.I:
            pass
        elif self.encoding == Encodings.O:
            pass
        elif self.encoding == Encodings.OI:
            pass
        elif self.encoding == Encodings.FD:
            pass
        elif self.encoding == Encodings.TD:
            pass
        elif self.encoding == Encodings.D:
            pass

        else:  # ZO encoding
            pass


# get the mnemonic of a modrm instruction, handling opcode extension if needed
def modrm_get_mnemonic(reg: int, instruction_info: InstructionInfo) -> str:

    # check opcode extension if it exists to get the mnemonic based on reg
    if instruction_info.extension_map and reg in instruction_info.extension_map:
        return instruction_info.extension_map[reg]
    # check if there is an illegal opcode extension
    elif instruction_info.extension_map:
        raise Exception(
            f"INVALID OPCODE EXTENSION {reg} FOR OPCODE {instruction_info.opcode:X}"
        )
    # return mnemonic directly from the instruction info
    else:
        return instruction_info.mnemonic


def modrm_get_addressing_mode(mod: int, instruction_info: InstructionInfo) -> int:
    if mod in instruction_info.addressing_modes:
        return mod
    else:
        raise Exception(
            f"INVALID ADDRESSING MODE {mod} FOR OPCODE {instruction_info.opcode:X}"
        )


# disassemble instruction with modrm
def modrm_disassemble(data: bytearray, opcode_size, instruction_info: InstructionInfo):
    # account for opcode size + modrm
    instruction_size = opcode_size + 1

    # parse the modrm byte
    (mod, reg, rm) = parse_modrm(data[0])

    # start building the instruction object
    instruction = Instruction(
        mnemonic=modrm_get_mnemonic(reg, instruction_info),
        encoding=instruction_info.encoding,
        reg=GLOBAL_REGISTER_NAMES[reg],
    )

    # safely get addressing mode
    mod = modrm_get_addressing_mode(mod, instruction_info)

    # TODO:displacement interaction with SIB
    # TODO: MOVE THIS LOGIC TO A NEW FUNCTION
    # TODO: endian swap on immediates and displacements

    # continue building instruction based on addressing mode:

    # r/m is a direct register
    if mod == 3:
        instruction.rm = GLOBAL_REGISTER_NAMES[rm]

    # r/m is register + dword displacement
    elif mod == 2:
        # sib byte detected
        if rm == 4:
            instruction_size += 5
            displacement = data[2:6]
            (scale, index, base) = parse_sib(data[1])
            instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[index]}*{scale} + {GLOBAL_REGISTER_NAMES[base]} + {displacement.hex()} ]"
        else:
            instruction_size += 4
            displacement = data[1:5]
            instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[rm]} + {displacement.hex()} ]"

    # rm is register + byte displacement
    elif mod == 1:
        # sib byte detected
        if rm == 4:
            instruction_size += 2
            displacement = data[2]
            (scale, index, base) = parse_sib(data[1])
            instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[index]}*{scale} + {GLOBAL_REGISTER_NAMES[base]} + {int(displacement)} ]"
        else:
            instruction_size += 1
            displacement = data[1]
            instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[rm]} + {int(displacement)} ]"

    # mod is 0, check special cases
    else:
        # r/m is a displacement32
        if rm == 5:
            instruction_size += 4
            displacement = data[1:5]
            instruction.rm = f"[ {displacement} ]"

        # sib byte
        elif rm == 4:
            instruction_size += 1
            (scale, index, base) = parse_sib(data[1])
            if base == 4:
                instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[index]}*{scale} ]"
            else:
                instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[index]}*{scale} + {base} ]"

        # register only
        else:
            instruction.rm = f"[{GLOBAL_REGISTER_NAMES[rm]}]"

    # handle an immediate in the case of an MI instruction
    if instruction_info.encoding == Encodings.MI:
        instruction.immediate = data[
            instruction_size : instruction_size + instruction_info.imm_size
        ]
        instruction_size += instruction_info.imm_size

    return instruction, instruction_size


# disassemble instruction with no modrm
def no_modrm_disassemble(data, opcode_size, instruction_info):
    # disassemble instruction with no modrm
    pass


def disassemble(data):
    # figure out the opcode and get a respective instruction data object

    # check for single byte opcode
    if data[0] in GLOBAL_INSTRUCTIONS_MAP:
        opcode_size = 1
        instruction_info = GLOBAL_INSTRUCTIONS_MAP[data[0]]

    # check for two byte opcode
    elif data[:2] in GLOBAL_INSTRUCTIONS_MAP:
        opcode_size = 2
        instruction_info = GLOBAL_INSTRUCTIONS_MAP[data[:2]]

    else:
        return Instruction(immediate=data[0], is_db=True), 1

    # check if modrm instruction
    if instruction_info.has_modrm:
        instruction, instruction_size = modrm_disassemble(
            data[opcode_size:], opcode_size, instruction_info
        )
    else:
        # instruction, instruction_size = no_modrm_disassemble(
        #     data[opcode_size:], opcode_size, instruction_info
        # )
        return Instruction(immediate=data[0], is_db=True), 1

    return instruction, instruction_size


# linnear sweep algorithm for disassembly
def linnear_sweep(filename: str):
    counter = 0
    output_list = {}
    labels = {}

    # get the binary data from the file
    data = get_file(filename)

    while counter < len(data):
        original_offset = counter

        # TODO: HANDLE FUNCTION CALLS / JUMPS

        # disassemble the instruction and get the instruction size
        instruction, instruction_size = disassemble(data[counter:])

        # store the instruction in the output list along with the raw bytes
        output_list[original_offset] = (
            instruction,
            data[original_offset : original_offset + instruction_size + 1],
        )

        counter += instruction_size

    return output_list, labels
