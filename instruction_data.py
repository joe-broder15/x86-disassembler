from enum import Enum


# data class that stores information about an instruction
class InstructionInfo:
    def __init__(
        self,
        opcode,
        mnemonic,
        has_modrm,
        encoding,
        extension_map=None,
        addressing_modes=[0, 1, 2, 3],
        opcode_plus=False,
        prefix_map=None,
        imm_size=4,
    ) -> None:
        self.opcode = opcode  # opcode of the instruction
        self.mnemonic = mnemonic  # mnemonic of the instruction
        self.has_modrm = has_modrm  # bool indicating whether it has a modrm
        self.addressing_modes = addressing_modes  # allowed addressing modes for modrm
        self.encoding = encoding  # encoding/format type
        self.extension_map = extension_map  # opcode extension map if extension exists
        self.opcode_plus = opcode_plus  # bool indicating whether we add to the opcode
        self.prefix_map = prefix_map  # map of prefixes for the instruction
        self.imm_size = imm_size  # immediate size


GLOBAL_REGISTER_NAMES = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]
REGADD_OPCODES = [0x48, 0x40, 0xB8, 0x58, 0x50]
CALL_GENERATING = {"jmp", "jz", "jnz", "call"}

Encodings = Enum(
    "Encodings",
    [
        "I",
        "MI",
        "MR",
        "RM",
        "M",
        "O",
        "OI",
        "D",
        "FD",
        "TD",
        "ZO",
    ],
)

# GLOBAL_INSTRUCTION_MAP
GLOBAL_INSTRUCTIONS_MAP = {
    # Add
    0x05: InstructionInfo(0x05, "add eax,", False, Encodings.I),
    0x01: InstructionInfo(0x01, "add", True, Encodings.MR),
    0x03: InstructionInfo(0x03, "add", True, Encodings.RM),
    # And
    0x25: InstructionInfo(0x25, "and eax,", False, Encodings.I),
    0x21: InstructionInfo(0x21, "and", True, Encodings.MR),
    0x23: InstructionInfo(0x23, "and", True, Encodings.RM),
    # Call
    0xE8: InstructionInfo(0xE8, "call", False, Encodings.D),
    # Clflush
    0xF0AE: InstructionInfo(
        0xF0AE,
        None,
        True,
        Encodings.M,
        extension_map={7: "clflush"},
        addressing_modes=[0, 1, 2],
    ),
    # Cmp
    0x3D: InstructionInfo(0x3D, "cmp eax,", False, Encodings.I),
    0x39: InstructionInfo(0x39, "cmp", True, Encodings.MR),
    0x3B: InstructionInfo(0x3B, "cmp", False, Encodings.RM),
    # Dec
    0x48: InstructionInfo(0x48, "dec", False, Encodings.O, opcode_plus=True),
    # Inc
    0x40: InstructionInfo(0x40, "inc", False, Encodings.O, opcode_plus=True),
    # Jmp
    0xEB: InstructionInfo(0xEB, "jmp", False, Encodings.D, imm_size=1),
    0xE9: InstructionInfo(0xE9, "jmp", False, Encodings.D),
    # Jz/Jnz
    0x74: InstructionInfo(0x74, "jz", False, Encodings.D, imm_size=1),
    0x75: InstructionInfo(0x75, "jnz", False, Encodings.D, imm_size=1),
    0x0F85: InstructionInfo(0x0F85, "jnz", False, Encodings.D),
    0x0F84: InstructionInfo(0x0F84, "jz", False, Encodings.D),
    # Lea
    0x8D: InstructionInfo(
        0x8D, "lea", True, Encodings.RM, addressing_modes=[0, 1, 2]
    ),  # addressing mode 0b11 is illegal
    # Mov
    0xA1: InstructionInfo(0xA1, "mov", False, Encodings.FD),
    0xA3: InstructionInfo(0xA3, "mov", False, Encodings.TD),
    0xB8: InstructionInfo(0xB8, "mov", False, Encodings.OI),
    0xC7: InstructionInfo(0xC7, None, True, Encodings.MI, extension_map={0: "mov"}),
    0x89: InstructionInfo(0x89, "mov", True, Encodings.MR),
    0x8B: InstructionInfo(0x8B, "mov", True, Encodings.RM),
    # Movsd
    0xA5: InstructionInfo(0xA5, "movsd", False, Encodings.ZO),
    # Nop
    0x90: InstructionInfo(0x90, "nop", False, Encodings.ZO),
    # Or
    0x0D: InstructionInfo(0x0D, "or eax,", False, Encodings.I),
    0x09: InstructionInfo(0x09, "or", True, Encodings.MR),
    0x0B: InstructionInfo(0x0B, "or", True, Encodings.RM),
    # Pop
    0x8F: InstructionInfo(0x8F, None, True, Encodings.M, extension_map={0: "pop"}),
    0x58: InstructionInfo(0x58, "pop", False, Encodings.O),
    # Push
    0x50: InstructionInfo(0x50, "push", False, Encodings.O),
    0x68: InstructionInfo(0x68, "push", False, Encodings.I),
    0x6A: InstructionInfo(0x6A, "push", False, Encodings.I, imm_size=1),
    # Repne cmpsd
    0xF2A7: InstructionInfo(0xF2A7, "repne cmpsd", False, Encodings.ZO),
    # ret/retn/retf
    0xCB: InstructionInfo(0xCB, "retf", False, Encodings.ZO),
    0xCA: InstructionInfo(0xCA, "retf", False, Encodings.I, imm_size=2),
    0xC3: InstructionInfo(0xC3, "retn", False, Encodings.ZO),
    0xC2: InstructionInfo(0xC2, "retn", False, Encodings.I, imm_size=2),
    # Sub
    0x2D: InstructionInfo(0x2D, "sub", True, Encodings.I),
    0x29: InstructionInfo(0x29, "sub", True, Encodings.MR),
    0x2B: InstructionInfo(0x2B, "sub", True, Encodings.RM),
    # Test
    0xA9: InstructionInfo(0xA9, "test eax,", False, Encodings.I),
    0x85: InstructionInfo(0x85, "test", True, Encodings.MR),
    # Xor
    0x35: InstructionInfo(0x35, "xor eax,", False, Encodings.I),
    0x31: InstructionInfo(0x31, "xor", True, Encodings.MR),
    0x33: InstructionInfo(0x33, "xor", True, Encodings.RM),
    # Multi
    0xFF: InstructionInfo(
        0xFF,
        None,
        True,
        Encodings.M,
        extension_map={0: "inc", 1: "dec", 2: "call", 4: "jmp", 6: "push"},
    ),
    0x81: InstructionInfo(
        0x81,
        None,
        True,
        Encodings.MI,
        extension_map={0: "add", 1: "or", 4: "and", 5: "sub", 6: "xor", 7: "cmp"},
    ),
    0xF7: InstructionInfo(
        0xF7, None, True, Encodings.MI, extension_map={0: "test", 2: "not", 7: "idiv"}
    ),
}
