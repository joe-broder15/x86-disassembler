from instruction_data import GLOBAL_INSTRUCTIONS_MAP, InstructionInfo, Encodings
from byte_utils import parse_modrm, parse_sib, get_file


# simple data class for building up a disassembled instruction, will be printed later
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
        mnemonic = mnemonic
        encoding = encoding
        immediate = immediate
        reg = reg
        rm = rm
        scale = scale
        index = index
        base = base


# disassemble instruction with modrm
def disassemble_modrm(data, opcode_size, instruction_info: InstructionInfo):

    # account for opcode size + modrm
    instruction_size = opcode_size

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
    instruction = Instruction(mnemonic=mnemonic, encoding=instruction_info.encoding)

    if mod == 3:
        pass
    elif mod == 2:
        pass
    elif mod == 1:
        pass
    else:
        pass

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

        # TODO: HANDLE DB ILLEGAL OPCODES
        instruction, instruction_bytes, instruction_size = disassemble(data[counter:])

        output_list[original_offset] = (instruction, instruction_bytes)

        counter += instruction_size

    pass
