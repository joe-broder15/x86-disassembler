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
    ):
        self.mnemonic = mnemonic
        self.encoding = encoding
        self.immediate = immediate
        self.reg = reg
        self.rm = rm
        self.scale = scale
        self.index = index
        self.base = base

    def __str__(self) -> str:
        # TODO: HANDLE FORMATTING BASED ON ENCODING FOR PRINT
        return self.mnemonic


# disassemble instruction with modrm
def disassemble_modrm(data: bytearray, opcode_size, instruction_info: InstructionInfo):
    # account for opcode size + modrm
    instruction_size = opcode_size + 1

    # parse the modrm byte
    (mod, reg, rm) = parse_modrm(data[0])

    # get mnemonic
    mnemonic = instruction_info.mnemonic

    # check opcode extension if it exists to get the mnemonic
    if instruction_info.extension_map:
        if reg in instruction_info.extension_map:
            mnemonic = instruction_info.extension_map[reg]
        else:
            raise Exception(
                f"INVALID OPCODE EXTENSION {reg} FOR OPCODE {instruction_info.opcode}"
            )

    # check for an illegal addressing mode
    if not mod in instruction_info.addressing_modes:
        raise Exception(
            f"INVALID ADDRESSING MODE {mod} FOR OPCODE {instruction_info.opcode}"
        )

    # start building the instruction object
    instruction = Instruction(
        mnemonic=mnemonic, encoding=instruction_info.encoding, reg=reg
    )

    # build instruction based on addressing mode
    # r/m is a direct register
    if mod == 3:
        instruction.rm = GLOBAL_REGISTER_NAMES[rm]

    # TODO:displacement interaction with SIB

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
            instruction.reg = GLOBAL_REGISTER_NAMES[reg]
            instruction.rm = f"[{GLOBAL_REGISTER_NAMES[rm]}]"

    return instruction, instruction_size


# disassemble instruction with no modrm
def disassemble_no_modrm(data, opcode_size, instruction_info):
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

    # unknown opcode, return a db
    # TODO: HANDLE DB ILLEGAL OPCODE
    else:
        raise Exception("unknown opcode")

    # check if modrm instruction
    if instruction_info.has_modrm:
        instruction, instruction_size = disassemble_modrm(
            data[opcode_size:], opcode_size, instruction_info
        )
    else:
        instruction, instruction_size = disassemble_no_modrm(
            data[opcode_size:], opcode_size, instruction_info
        )

    return instruction, data[:instruction_size], instruction_size


def linnear_sweep(filename: str):
    counter = 0x0
    output_list = {}
    labels = {}

    # get the binary data from the file
    data = get_file(filename)

    while counter < len(data):
        original_offset = counter

        # TODO: HANDLE FUNCTION CALLS / JUMPS
        instruction, instruction_bytes, instruction_size = disassemble(data[counter:])

        output_list[original_offset] = (instruction, instruction_bytes)

        counter += instruction_size

    pass
