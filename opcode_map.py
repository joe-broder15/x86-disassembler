# Key is the opcode
# value is a list of useful information
GLOBAL_OPCODE_MAP = {
    # Add
    0x05: ["add eax, ", False, "id", None],
    0x81: [
        None,
        True,
        "mi",
        {0: "add", 1: "or", 2: "adc", 3: "sbb", 4: "and", 5: "sub", 6: "xor", 7: "cmp"},
    ],
    0x01: ["add ", True, "mr", None],
    0x03: ["add ", True, "rm", None],

    # And
    0x25: ["and eax, ", False, "id", None],
    0x21: ["and ", True, "mr", None],
    0x23: ["and ", True, "rm", None],
    
    # Call
    0xE8: ["call ", False, "cd", None],
    0xFF: [
        None,
        True,
        "m",
        {2: "call", 4: "jmp"},
    ],
    # Clflush
    0x0F: [None, True, "m", {0xAE: "clflush"}],
    # Cmp
    0x3D: ["cmp eax, ", False, "id", None],
    0x39: ["cmp ", True, "mr", None],
    0x3B: ["cmp ", True, "rm", None],
    # Dec
    0xFF: [None, True, "m", {1: "dec"}],
    0x48: ["dec ", False, "rd", None],
    # Id
    0xF7: [None, True, "m", {7: "idiv"}],
    # Inc
    0xFF: [None, True, "m", {0: "inc"}],
    0x40: ["inc ", False, "rd", None],
    # Jmp
    0xEB: ["jmp ", False, "cb", None],
    0xE9: ["jmp ", False, "cd", None],
    # Jz and Jnz
    0x74: ["jz ", False, "cb", None],
    0x75: ["jnz ", False, "cb", None],
    0x0F: [None, True, "cd", {0x84: "jz", 0x85: "jnz"}],
    # Lea
    0x8D: ["lea ", True, "rm", None],
    # Mov
    0xA1: ["mov eax, [", False, "moffs32", None],
    0xA3: ["mov [", False, "moffs32", None],
    0xB8: ["mov ", False, "rd", None],  # mov r32, imm32
    0xC7: ["mov ", True, "mi", None],  # mov r/m32, imm32
    0x89: ["mov ", True, "mr", None],  # mov r/m32, r32
    0x8B: ["mov ", True, "rm", None],  # mov r32, r/m32
    # Movsd
    0xA5: ["movsd", False, "m", None],
    # Nop
    0x90: ["nop", False, None, None],
    # Not
    0xF7: [None, True, "m", {2: "not"}],
    # Or
    0x0D: ["or eax, ", False, "id", None],
    0x09: ["or ", True, "mr", None],
    0x0B: ["or ", True, "rm", None],
    # Pop
    0x8F: ["pop ", True, "m", {0: "pop"}],
    0x58: ["pop ", False, "rd", None],
    # Push
    0xFF: [None, True, "m", {6: "push"}],
    0x50: ["push ", False, "rd", None],
    0x68: ["push ", False, "id", None],  # push imm32
    0x6A: ["push ", False, "ib", None],  # push imm8
    # Repne cmpsd
    0xF2: [None, True, "m", {0xA7: "repne cmpsd"}],
    # Retf and retn
    0xCB: ["retf", False, None, None],
    0xCA: ["retf ", False, "iw", None],  # retf imm16
    0xC3: ["retn", False, None, None],
    0xC2: ["retn ", False, "iw", None],  # retn imm16
    # Sub
    0x2D: ["sub eax, ", False, "id", None],
    0x29: ["sub ", True, "mr", None],
    0x2B: ["sub ", True, "rm", None],
    # Test
    0xA9: ["test eax, ", False, "id", None],
    0x85: ["test ", True, "rm", None],
    # Xor
    0x35: ["xor eax, ", False, "id", None],
    0x31: ["xor ", True, "mr", None],
    0x33: ["xor ", True, "rm", None],
}
