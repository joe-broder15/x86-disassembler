from enum import Enum

# data class that stores information about an instruction
class InstructionData:

    def __init__(
        self,
        opcode,
        mnemonic,
        hasModRM,
        encoding,
        extension_map=None,
        addressingModes=[0, 1, 2, 3],
        opcode_plus=False,
        prefix_map=None,
        imm_size=32,
    ) -> None:
        self.opcode = opcode  # opcode of the instruction
        self.mnemonic = mnemonic  # mnemonic of the instruction
        self.hasModRM = hasModRM  # bool indicating whether it has a modrm
        self.addressingModes = addressingModes  # allowed addressing modes for modrm
        self.encoding = encoding  # encoding/format type
        self.extension_map = extension_map  # opcode extension map if extension exists
        self.opcode_plus = opcode_plus  # bool indicating whether we add to the opcode
        self.prefix_map = prefix_map  # map of prefixes for the instruction
        imm_size = imm_size  # immediate size


GLOBAL_REGISTER_NAMES = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]
GLOBAL_ENCODING_TYPES = ["id", "ib", "m", "rm", "mr", "cd", "cb", "mi", "o", "oi", "zo"]

# Encodings = Enum('Encodings', ["ID"])

# GLOBAL_INSTRUCTION_MAP
GLOBAL_INSTRUCTIONS_MAP = {
    # Add
    0x05: InstructionData(0x05, "add eax", False, "I"),
    0x01: InstructionData(0x01, "add", True, "MR"),
    0x03: InstructionData(0x03, "add", True, "RM"),

    # And
    0x25: InstructionData(0x25, "and eax", False, "I"),
    0x21: InstructionData(0x21, "and", True, "MR"),
    0x23: InstructionData(0x23, "and", True, "RM"),

    # Call
    0xE8: InstructionData(0xE8, "call", False, "D"),

    # Cmp
    0x3D: InstructionData(0x3D, "cmp eax", False, "I"),
    0x39: InstructionData(0x39, "cmp", True, "MR"),
    0x3B: InstructionData(0x3B, "cmp", False, "RM"),

    # Dec
    0x48: InstructionData(0x48, "dec", False, "O", opcode_plus=True),

    # Inc
    0x40: InstructionData(0x40, "inc", False, "O", opcode_plus=True),

    # Jmp
    0xEB: InstructionData(0xEB, "jmp", False, "D", imm_size=8),
    0xE9: InstructionData(0xE9, "jmp", False, "D"),

    # Jz/Jnz
    0x74: InstructionData(0x74, "jz", False, "D", imm_size=8),
    0x75: InstructionData(0x75, "jnz", False, "D", imm_size=8),

    # Lea
    0x8D: InstructionData(
        0x8D, "lea", True, "RM", addressingModes=[0, 1, 2]
    ),  # addressing mode 0b11 is illegal
    
    # Mov
    0xA1: InstructionData(0xA1, "mov"),  # special TODO
    0xA3: InstructionData(0xA3, "mov"),  # special TODO
    0xB8: InstructionData(0xB8, "mov", False, "OI"),
    0xC7: InstructionData(0xC7, None, True, "MI", extension_map={0: "mov"}),
    0x89: InstructionData(0x89, "mov", True, "MR"),
    0x8B: InstructionData(0x8B, "mov", True, "RM"),

    # Movsd
    0xA5: InstructionData(0xA5, "movsd", False, "ZO"),

    # Nop
    0x90: InstructionData(0x90, "nop", False, "ZO"),

    # Or
    0x0D: InstructionData(0x0D, "or eax", False, "I"),
    0x09: InstructionData(0x09, "or", True, "MR"),
    0x0B: InstructionData(0x0B, "or", True, "RM"),

    # Pop
    0x8F: InstructionData(0x8F, None, True, "M", extension_map={0: "pop"}),
    0x58: InstructionData(0x58, "pop", False, "O"),

    # Push
    0x50: InstructionData(0x50, "push", False, "O"),
    0x68: InstructionData(0x68, "push", False, "I"),
    0x6A: InstructionData(0x6A, "push", False, "I", imm_size=8),

    # ret/retn/retf
    0xCB: InstructionData(0xCB, "retf", False, "ZO"),
    0xCA: InstructionData(0xCA, "retf", False, "I", imm_size=16),
    0xC3: InstructionData(0xC3, "retn", False, "ZO"),
    0xC2: InstructionData(0xC2, "retn", False, "I", imm_size=16),

    # Sub
    0x2D: InstructionData(0x2D, "sub", True,"mi" ),
    0x29: InstructionData(0x29, "sub", True,"mr" ),
    0x2B: InstructionData(0x2B, "sub", True,"rm" ),

    # Test
    0xA9: InstructionData(0xA9, "test eax", False, "id"),
    0x85: InstructionData(0x85, "test", True, "mr"),

    # Xor
    0x35:InstructionData(0x35, "xor eax", False, "id"),
    0x31:InstructionData(0x31, "xor", True, "mr"),
    0x33:InstructionData(0x33, "xor", True, "rm"),

    # Multi
    0xFF: InstructionData(
        0xFF, None, True, "M", extension_map={0: "inc", 1:"dec", 2: "call", 4: "jmp", 6: "push"}
    ),
    0x81: InstructionData(
        0x81, None, True, "MI", extension_map={0: "add", 1:"or", 4: "and", 5:"sub", 6:"xor", 7: "cmp"}, imm_size=32
    ),
    0xF7: InstructionData(0xF7, None, True, "m", extension_map={0:"test", 2: "not", 7: "idiv"}),
    # TODO
    # clflush m8
    # jz/jnz rel32
    # repne cmpsd
}
