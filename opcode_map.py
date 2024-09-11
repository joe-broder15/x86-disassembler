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

Encodings = Enum('Encodings', ["I", "MI", "MR", "RM", "M", "O", "OI", "D", "FD", "TD", "ZO"])

# GLOBAL_INSTRUCTION_MAP
GLOBAL_INSTRUCTIONS_MAP = {
    # Add
    0x05: InstructionData(0x05, "add eax", False, Encodings.I),
    0x01: InstructionData(0x01, "add", True, Encodings.MR),
    0x03: InstructionData(0x03, "add", True, Encodings.RM),
    # And
    0x25: InstructionData(0x25, "and eax", False, Encodings.I),
    0x21: InstructionData(0x21, "and", True, Encodings.MR),
    0x23: InstructionData(0x23, "and", True, Encodings.RM),
    # Call
    0xE8: InstructionData(0xE8, "call", False, Encodings.D),
    # Clflush
    0xF0AE: InstructionData(
        0xF0AE, None, True, Encodings.M, extension_map={7: "clflush"}, addressingModes=[0, 1, 2]
    ),
    # Cmp
    0x3D: InstructionData(0x3D, "cmp eax", False, Encodings.I),
    0x39: InstructionData(0x39, "cmp", True, Encodings.MR),
    0x3B: InstructionData(0x3B, "cmp", False, Encodings.RM),
    # Dec
    0x48: InstructionData(0x48, "dec", False, Encodings.O, opcode_plus=True),
    # Inc
    0x40: InstructionData(0x40, "inc", False, Encodings.O, opcode_plus=True),
    # Jmp
    0xEB: InstructionData(0xEB, "jmp", False, Encodings.D, imm_size=8),
    0xE9: InstructionData(0xE9, "jmp", False, Encodings.D),
    # Jz/Jnz
    0x74: InstructionData(0x74, "jz", False, Encodings.D, imm_size=8),
    0x75: InstructionData(0x75, "jnz", False, Encodings.D, imm_size=8),
    0x0F85: InstructionData(0x0F85, "jnz", False, Encodings.D),
    0x0F84: InstructionData(0x0F84, "jz", False, Encodings.D),
    # Lea
    0x8D: InstructionData(
        0x8D, "lea", True, Encodings.RM, addressingModes=[0, 1, 2]
    ),  # addressing mode 0b11 is illegal
    # Mov
    0xA1: InstructionData(0xA1, "mov", False, Encodings.FD), 
    0xA3: InstructionData(0xA3, "mov", False, Encodings.TD),
    0xB8: InstructionData(0xB8, "mov", False, Encodings.OI),
    0xC7: InstructionData(0xC7, None, True, Encodings.MI, extension_map={0: "mov"}),
    0x89: InstructionData(0x89, "mov", True, Encodings.MR),
    0x8B: InstructionData(0x8B, "mov", True, Encodings.RM),
    # Movsd
    0xA5: InstructionData(0xA5, "movsd", False, Encodings.ZO),
    # Nop
    0x90: InstructionData(0x90, "nop", False, Encodings.ZO),
    # Or
    0x0D: InstructionData(0x0D, "or eax", False, Encodings.I),
    0x09: InstructionData(0x09, "or", True, Encodings.MR),
    0x0B: InstructionData(0x0B, "or", True, Encodings.RM),
    # Pop
    0x8F: InstructionData(0x8F, None, True, Encodings.M, extension_map={0: "pop"}),
    0x58: InstructionData(0x58, "pop", False, Encodings.O),
    # Push
    0x50: InstructionData(0x50, "push", False, Encodings.O),
    0x68: InstructionData(0x68, "push", False, Encodings.I),
    0x6A: InstructionData(0x6A, "push", False, Encodings.I, imm_size=8),
    # Repne cmpsd
    0xF2A7: InstructionData(0xF2A7, "repne cmpsd", False, Encodings.ZO),
    # ret/retn/retf
    0xCB: InstructionData(0xCB, "retf", False, Encodings.ZO),
    0xCA: InstructionData(0xCA, "retf", False, Encodings.I, imm_size=16),
    0xC3: InstructionData(0xC3, "retn", False, Encodings.ZO),
    0xC2: InstructionData(0xC2, "retn", False, Encodings.I, imm_size=16),
    # Sub
    0x2D: InstructionData(0x2D, "sub", True, Encodings.I),
    0x29: InstructionData(0x29, "sub", True, Encodings.MR),
    0x2B: InstructionData(0x2B, "sub", True, Encodings.RM),
    # Test
    0xA9: InstructionData(0xA9, "test eax", False, Encodings.I),
    0x85: InstructionData(0x85, "test", True, Encodings.MR),
    # Xor
    0x35: InstructionData(0x35, "xor eax", False, Encodings.I),
    0x31: InstructionData(0x31, "xor", True, Encodings.MR),
    0x33: InstructionData(0x33, "xor", True, Encodings.RM),
    # Multi
    0xFF: InstructionData(
        0xFF,
        None,
        True,
        Encodings.M,
        extension_map={0: "inc", 1: "dec", 2: "call", 4: "jmp", 6: "push"},
    ),
    0x81: InstructionData(
        0x81,
        None,
        True,
        Encodings.MI,
        extension_map={0: "add", 1: "or", 4: "and", 5: "sub", 6: "xor", 7: "cmp"}
    ),
    0xF7: InstructionData(
        0xF7, None, True, Encodings.MI, extension_map={0: "test", 2: "not", 7: "idiv"}
    ),
}
