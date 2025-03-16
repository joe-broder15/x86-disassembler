from enum import Enum


# InstructionInfo: Data class that stores information about an x86 instruction
# Used instead of a list because named fields are easier to track than indices
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
        self.opcode = opcode          # Numeric opcode value (e.g., 0x01, 0x89)
        self.mnemonic = mnemonic      # Assembly instruction name (e.g., "mov", "add")
        self.has_modrm = has_modrm    # Whether instruction uses ModR/M byte
        self.addressing_modes = addressing_modes  # Valid ModR/M addressing modes (0-3)
        self.encoding = encoding      # Instruction format (I, MR, RM, etc.)
        self.extension_map = extension_map  # Maps ModR/M.reg field to specific instructions
        self.opcode_plus = opcode_plus  # Whether register is encoded in opcode (e.g., 0x40-0x47 for inc)
        self.prefix_map = prefix_map  # Maps instruction prefixes to variants
        self.imm_size = imm_size      # Size of immediate value in bytes (1, 2, or 4)


# List of x86 32-bit register names in order of their encoding (0-7)
GLOBAL_REGISTER_NAMES = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]

# Opcodes that encode the register in the opcode itself
REGADD_OPCODES = [0x48, 0x40, 0xB8, 0x58, 0x50]

# Enum defining instruction encoding types:
# I   = Immediate operand
# MI  = ModR/M + Immediate
# MR  = ModR/M (destination) + Register (source)
# RM  = Register (destination) + ModR/M (source)
# M   = ModR/M only
# O   = Opcode + Register encoding
# OI  = Opcode + Register + Immediate
# D   = Relative displacement/address
# FD  = Fixed displacement (direct memory)
# TD  = Target displacement
# ZO  = Zero operands (implied)
ENCODINGS = Enum(
    "ENCODINGS",
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

# Dictionary mapping opcodes to their corresponding instruction information
# Organized by instruction groups for readability
GLOBAL_INSTRUCTIONS_MAP = {
    # Add instructions
    0x05: InstructionInfo(0x05, "add eax,", False, ENCODINGS.I),      # add eax, imm32
    0x01: InstructionInfo(0x01, "add", True, ENCODINGS.MR),           # add r/m32, r32
    0x03: InstructionInfo(0x03, "add", True, ENCODINGS.RM),           # add r32, r/m32
    
    # And instructions
    0x25: InstructionInfo(0x25, "and eax,", False, ENCODINGS.I),      # and eax, imm32
    0x21: InstructionInfo(0x21, "and", True, ENCODINGS.MR),           # and r/m32, r32
    0x23: InstructionInfo(0x23, "and", True, ENCODINGS.RM),           # and r32, r/m32
    
    # Call instruction
    0xE8: InstructionInfo(0xE8, "call", False, ENCODINGS.D),          # call rel32
    
    # Clflush instruction (cache line flush)
    0x0FAE: InstructionInfo(
        0x0FAE,
        None,
        True,
        ENCODINGS.M,
        extension_map={7: "clflush"},                                 # clflush m8
        addressing_modes=[0, 1, 2],                                   # No register operands allowed
    ),
    
    # Compare instructions
    0x3D: InstructionInfo(0x3D, "cmp eax,", False, ENCODINGS.I),      # cmp eax, imm32
    0x39: InstructionInfo(0x39, "cmp", True, ENCODINGS.MR),           # cmp r/m32, r32
    0x3B: InstructionInfo(0x3B, "cmp", True, ENCODINGS.RM),           # cmp r32, r/m32
    
    # Decrement instruction
    0x48: InstructionInfo(0x48, "dec", False, ENCODINGS.O, opcode_plus=True),  # dec r32
    
    # Increment instruction
    0x40: InstructionInfo(0x40, "inc", False, ENCODINGS.O, opcode_plus=True),  # inc r32
    
    # Jump instructions
    0xEB: InstructionInfo(0xEB, "jmp", False, ENCODINGS.D, imm_size=1),  # jmp rel8
    0xE9: InstructionInfo(0xE9, "jmp", False, ENCODINGS.D),           # jmp rel32
    
    # Conditional jump instructions
    0x74: InstructionInfo(0x74, "jz", False, ENCODINGS.D, imm_size=1),   # jz rel8
    0x75: InstructionInfo(0x75, "jnz", False, ENCODINGS.D, imm_size=1),  # jnz rel8
    0x0F85: InstructionInfo(0x0F85, "jnz", False, ENCODINGS.D),       # jnz rel32
    0x0F84: InstructionInfo(0x0F84, "jz", False, ENCODINGS.D),        # jz rel32
    
    # Load effective address
    0x8D: InstructionInfo(
        0x8D, "lea", True, ENCODINGS.RM, addressing_modes=[0, 1, 2]   # lea r32, m
    ),  # addressing mode 0b11 is illegal (can't use register as source)
    
    # Move instructions
    0xA1: InstructionInfo(0xA1, "mov", False, ENCODINGS.FD),          # mov eax, moffs32
    0xA3: InstructionInfo(0xA3, "mov", False, ENCODINGS.TD),          # mov moffs32, eax
    0xB8: InstructionInfo(0xB8, "mov", False, ENCODINGS.OI),          # mov r32, imm32
    0xC7: InstructionInfo(0xC7, None, True, ENCODINGS.MI, extension_map={0: "mov"}),  # mov r/m32, imm32
    0x89: InstructionInfo(0x89, "mov", True, ENCODINGS.MR),           # mov r/m32, r32
    0x8B: InstructionInfo(0x8B, "mov", True, ENCODINGS.RM),           # mov r32, r/m32
    
    # Move string doubleword
    0xA5: InstructionInfo(0xA5, "movsd", False, ENCODINGS.ZO),        # movsd
    
    # No operation
    0x90: InstructionInfo(0x90, "nop", False, ENCODINGS.ZO),          # nop
    
    # Logical OR instructions
    0x0D: InstructionInfo(0x0D, "or eax,", False, ENCODINGS.I),       # or eax, imm32
    0x09: InstructionInfo(0x09, "or", True, ENCODINGS.MR),            # or r/m32, r32
    0x0B: InstructionInfo(0x0B, "or", True, ENCODINGS.RM),            # or r32, r/m32
    
    # Pop instructions
    0x8F: InstructionInfo(0x8F, None, True, ENCODINGS.M, extension_map={0: "pop"}),  # pop r/m32
    0x58: InstructionInfo(0x58, "pop", False, ENCODINGS.O),           # pop r32
    
    # Push instructions
    0x50: InstructionInfo(0x50, "push", False, ENCODINGS.O),          # push r32
    0x68: InstructionInfo(0x68, "push", False, ENCODINGS.I),          # push imm32
    0x6A: InstructionInfo(0x6A, "push", False, ENCODINGS.I, imm_size=1),  # push imm8
    
    # Repeat string operations
    0xF2A7: InstructionInfo(0xF2A7, "repne cmpsd", False, ENCODINGS.ZO),  # repne cmpsd
    
    # Return instructions
    0xCB: InstructionInfo(0xCB, "retf", False, ENCODINGS.ZO),         # retf (far return)
    0xCA: InstructionInfo(0xCA, "retf", False, ENCODINGS.I, imm_size=2),  # retf imm16
    0xC3: InstructionInfo(0xC3, "retn", False, ENCODINGS.ZO),         # retn (near return)
    0xC2: InstructionInfo(0xC2, "retn", False, ENCODINGS.I, imm_size=2),  # retn imm16
    
    # Subtract instructions
    0x2D: InstructionInfo(0x2D, "sub", False, ENCODINGS.I),           # sub eax, imm32
    0x29: InstructionInfo(0x29, "sub", True, ENCODINGS.MR),           # sub r/m32, r32
    0x2B: InstructionInfo(0x2B, "sub", True, ENCODINGS.RM),           # sub r32, r/m32
    
    # Test instructions
    0xA9: InstructionInfo(0xA9, "test eax,", False, ENCODINGS.I),     # test eax, imm32
    0x85: InstructionInfo(0x85, "test", True, ENCODINGS.MR),          # test r/m32, r32
    
    # Logical XOR instructions
    0x35: InstructionInfo(0x35, "xor eax,", False, ENCODINGS.I),      # xor eax, imm32
    0x31: InstructionInfo(0x31, "xor", True, ENCODINGS.MR),           # xor r/m32, r32
    0x33: InstructionInfo(0x33, "xor", True, ENCODINGS.RM),           # xor r32, r/m32
    
    # Multi-purpose opcodes that use ModR/M.reg field to determine the actual instruction
    0xFF: InstructionInfo(
        0xFF,
        None,
        True,
        ENCODINGS.M,
        extension_map={0: "inc", 1: "dec", 2: "call", 4: "jmp", 6: "push"},  # Various operations based on ModR/M.reg
    ),
    0x81: InstructionInfo(
        0x81,
        None,
        True,
        ENCODINGS.MI,
        extension_map={0: "add", 1: "or", 4: "and", 5: "sub", 6: "xor", 7: "cmp"},  # Immediate operations
    ),
    0xF7: InstructionInfo(
        0xF7, None, True, ENCODINGS.M, extension_map={0: "test", 2: "not", 7: "idiv"}  # Unary operations
    ),
}
