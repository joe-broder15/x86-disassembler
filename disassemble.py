from instruction_data import (
    GLOBAL_INSTRUCTIONS_MAP,
    GLOBAL_REGISTER_NAMES,
    REGADD_OPCODES,
    InstructionInfo,
    ENCODINGS,
)
from byte_utils import parse_modrm, parse_sib, get_file, to_signed
from typing import Tuple, Optional, Dict, List


# Instruction class represents a disassembled x86 instruction with all its components
class Instruction:
    def __init__(
        self,
        mnemonic=None,        # The instruction name (e.g., "mov", "add")
        encoding=None,        # The instruction encoding type (e.g., MR, RM, I)
        immediate=None,       # Immediate value operand
        reg=None,             # Register operand
        rm=None,              # ModR/M operand (memory or register)
        scale=None,           # SIB scale factor
        index=None,           # SIB index register
        base=None,            # SIB base register
        is_db=False,          # Flag for data byte (invalid instruction)
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

    # Format the instruction as an assembly language string based on its encoding type
    def __str__(self) -> str:

        # Handle data byte (invalid instruction)
        if self.is_db:
            return f"db 0x{self.immediate:02X}"

        # Format instruction based on its encoding type
        if self.encoding == ENCODINGS.M:
            # ModR/M only (e.g., "inc [eax]")
            return f"{self.mnemonic} {self.rm}"
        elif self.encoding == ENCODINGS.MI:
            # ModR/M + Immediate (e.g., "add [eax], 0x10")
            return f"{self.mnemonic} {self.rm}, {self.immediate}"
        elif self.encoding == ENCODINGS.MR:
            # ModR/M destination, Register source (e.g., "mov [eax], ecx")
            return f"{self.mnemonic} {self.rm}, {self.reg}"
        elif self.encoding == ENCODINGS.RM:
            # Register destination, ModR/M source (e.g., "mov eax, [ecx]")
            return f"{self.mnemonic} {self.reg}, {self.rm}"
        elif self.encoding == ENCODINGS.I:
            # Immediate operand (e.g., "push 0x10")
            return f"{self.mnemonic} {self.immediate}"
        elif self.encoding == ENCODINGS.O:
            # Opcode + Register encoding (e.g., "inc eax")
            return f"{self.mnemonic} {self.reg}"
        elif self.encoding == ENCODINGS.OI:
            # Opcode + Register + Immediate (e.g., "mov eax, 0x10")
            return f"{self.mnemonic} {self.reg}, {self.immediate}"
        elif self.encoding == ENCODINGS.FD:
            # Fixed displacement (e.g., "mov eax, [0x401000]")
            return f"{self.mnemonic} {self.reg}, {self.immediate}"
        elif self.encoding == ENCODINGS.TD:
            # Target displacement (e.g., "mov [0x401000], eax")
            return f"{self.mnemonic} {self.immediate}, {self.reg}"
        elif self.encoding == ENCODINGS.D:
            # Relative displacement (e.g., "jmp 0x401000")
            return f"{self.mnemonic} {self.immediate}"
        else:  # ENCODINGS.ZO - Zero operands (implied)
            # No operands (e.g., "ret", "nop")
            return self.mnemonic


# Get the instruction mnemonic for instructions that use ModR/M byte
# Some opcodes use the reg field of ModR/M to determine the actual instruction
def modrm_get_mnemonic(reg: int, instruction_info: InstructionInfo) -> str:

    # If this opcode uses reg field for extension, get the mnemonic from the extension map
    if instruction_info.extension_map and reg in instruction_info.extension_map:
        return instruction_info.extension_map[reg]

    # If extension map exists but reg value is not valid, raise an exception
    elif instruction_info.extension_map:
        raise Exception(
            f"Invalid opcode extension {reg} for opcode {instruction_info.opcode:X}"
        )

    # Otherwise, use the mnemonic directly from instruction_info
    else:
        return instruction_info.mnemonic


# Verify that the addressing mode (mod field) is valid for this instruction
def modrm_get_addressing_mode(mod: int, instruction_info: InstructionInfo) -> int:
    if mod in instruction_info.addressing_modes:
        return mod
    else:
        raise Exception(
            f"Invalid addressing mode {mod} for opcode {instruction_info.opcode:X}"
        )


# Disassemble an instruction that uses the ModR/M byte
def modrm_disassemble(data: bytearray, opcode_size, instruction_info: InstructionInfo):

    # Total instruction size starts with opcode + ModR/M byte
    instruction_size = opcode_size + 1

    # Parse the ModR/M byte into its components
    (mod, reg, rm) = parse_modrm(data[0])

    # Start building the instruction object with the mnemonic and register operand
    instruction = Instruction(
        mnemonic=modrm_get_mnemonic(reg, instruction_info),
        encoding=instruction_info.encoding,
        reg=GLOBAL_REGISTER_NAMES[reg],
    )

    # Special case: F7 opcode with "test" mnemonic uses MI encoding instead
    if instruction_info.opcode == 0xF7 and instruction.mnemonic == "test":
        instruction.encoding = ENCODINGS.MI

    # Verify the addressing mode is valid for this instruction
    mod = modrm_get_addressing_mode(mod, instruction_info)

    # Process the ModR/M byte based on addressing mode:

    # Mode 3: Direct register addressing (no memory operand)
    if mod == 3:
        instruction.rm = GLOBAL_REGISTER_NAMES[rm]

    # Mode 2: Register + 32-bit displacement
    elif mod == 2:
        # Check for SIB byte (Scale-Index-Base)
        if rm == 4:
            instruction_size += 5  # opcode + modrm + sib + disp32
            displacement = int.from_bytes(data[2:6], "little", signed=False)
            (scale, index, base) = parse_sib(data[1])
            # ESP (index=4) can't be used as an index register
            if index == 4:
                instruction.rm = f"[ dword {GLOBAL_REGISTER_NAMES[base]}"
            else:
                instruction.rm = f"[ dword {GLOBAL_REGISTER_NAMES[index]}*{scale} + {GLOBAL_REGISTER_NAMES[base]}"
        else:
            # Regular register + displacement
            instruction_size += 4  # opcode + modrm + disp32
            displacement = int.from_bytes(data[1:5], "little", signed=False)
            instruction.rm = f"[ dword {GLOBAL_REGISTER_NAMES[rm]}"

        # Add displacement if non-zero
        if not displacement == 0:
            instruction.rm += f" + 0x{displacement:08X}"

        instruction.rm += " ]"

    # Mode 1: Register + 8-bit displacement
    elif mod == 1:
        # Check for SIB byte
        if rm == 4:
            instruction_size += 2  # opcode + modrm + sib + disp8
            displacement = to_signed(data[2])
            (scale, index, base) = parse_sib(data[1])
            # ESP (index=4) can't be used as an index register
            if index == 4:
                instruction.rm = f"[ byte {GLOBAL_REGISTER_NAMES[base]}"
            else:
                instruction.rm = f"[ byte {GLOBAL_REGISTER_NAMES[index]}*{scale} + {GLOBAL_REGISTER_NAMES[base]}"
        else:
            # Regular register + displacement
            instruction_size += 1  # opcode + modrm + disp8
            displacement = to_signed(data[1])
            instruction.rm = f"[ byte {GLOBAL_REGISTER_NAMES[rm]}"

        # Add displacement with sign if non-zero
        if not displacement == 0:
            instruction.rm += (
                f" {"+" if displacement > 0 else "-"} 0x{abs(displacement):02X}"
            )

        instruction.rm += " ]"

    # Mode 0: Special cases and register indirect addressing
    else:
        # Special case: [disp32] when rm=5 and mod=0
        if rm == 5:
            instruction_size += 4  # opcode + modrm + disp32
            displacement = int.from_bytes(data[1:5], "little", signed=False)
            instruction.rm = f"[ 0x{displacement:08X} ]"

        # SIB byte present
        elif rm == 4:
            instruction_size += 1  # opcode + modrm + sib
            (scale, index, base) = parse_sib(data[1])
            
            # Special SIB cases for mod=0
            # ESP (index=4) can't be used as an index register
            if index == 4:
                instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[base]} ]"
            # Special case: base=5 (EBP) with mod=0 means disp32 with optional index
            elif base == 5:
                instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[index]}*{scale}"
                instruction_size += 4  # Add disp32
                displacement = int.from_bytes(data[2:6], "little", signed=False)
                if not displacement == 0:
                    instruction.rm += f" + 0x{displacement:08X}"
                instruction.rm += " ]"
            # Normal SIB case
            else:
                instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[index]}*{scale} + {GLOBAL_REGISTER_NAMES[base]} ]"

        # Regular register indirect addressing
        else:
            instruction.rm = f"[ {GLOBAL_REGISTER_NAMES[rm]} ]"

    # Handle immediate value for MI encoding (ModR/M + Immediate)
    if instruction.encoding == ENCODINGS.MI:
        # Read the immediate value based on its size
        instruction.immediate = int.from_bytes(
            data[
                instruction_size - 1 : instruction_size - 1 + instruction_info.imm_size
            ],
            "little",
            signed=False,
        )
        # Format 32-bit immediate as hex
        if instruction_info.imm_size == 4:
            instruction.immediate = f"0x{instruction.immediate:08X}"

        instruction_size += instruction_info.imm_size

    return instruction, instruction_size


# Disassemble instructions that don't use ModR/M byte or register-in-opcode encoding
def no_modrm_no_regadd_disassemble(
    data, opcode_size, instruction_info: InstructionInfo, offset
):
    # Initialize instruction size and create instruction object
    instruction_size = opcode_size
    instruction = Instruction(
        mnemonic=instruction_info.mnemonic, encoding=instruction_info.encoding
    )

    # Zero-operand instructions (like RET, NOP) don't need further processing
    if not instruction.encoding == ENCODINGS.ZO:

        # Handle special EAX-only instructions (like MOV EAX, [mem])
        if (
            instruction_info.encoding == ENCODINGS.TD
            or instruction_info.encoding == ENCODINGS.FD
        ):
            instruction.reg = "eax"

        # Add immediate size to total instruction size
        instruction_size += instruction_info.imm_size

        # Process immediate value based on encoding type
        if instruction.encoding == ENCODINGS.I:
            imm_size = instruction_info.imm_size
            if imm_size == 1:
                # For 1-byte immediate, read as a signed integer (for PUSH imm8, etc.)
                imm = int.from_bytes(data[:imm_size], byteorder="little", signed=True)
                instruction.immediate = f"{imm}"
            else:
                # For 2 or 4-byte immediate, read as an unsigned integer
                imm = int.from_bytes(data[:imm_size], byteorder="little", signed=False)
                # Format the immediate value as a hexadecimal string
                instruction.immediate = f"0x{imm:0{imm_size * 2}X}"

        # Handle relative offset for jump/call instructions (encoding D)
        else:
            # Calculate target address: current offset + instruction size + relative offset
            instruction.immediate = (
                int.from_bytes(data[: instruction_info.imm_size], "little", signed=True)
                + offset
                + instruction_size
            )

    return instruction, instruction_size


# Check if an opcode corresponds to one that encodes a register in the opcode itself
def regadd_check_opcode(opcode):
    # Check each potential register-in-opcode base value
    for regadd_opcode in REGADD_OPCODES:
        # If opcode is within range (base to base+7), it's encoding a register
        if (opcode - regadd_opcode >= 0) and (opcode - regadd_opcode < 8):
            return GLOBAL_INSTRUCTIONS_MAP[regadd_opcode]
    return None


# Disassemble instructions that encode the register in the opcode
def regadd_disassemble(data, instruction_info: InstructionInfo):
    # Ensure we have enough data
    if len(data) < 1:
        raise ValueError("Insufficient data for disassembly.")

    # Initialize instruction size and create instruction object
    instruction_size = 1
    
    # Calculate which register is encoded in the opcode (opcode difference gives register number)
    instruction = Instruction(
        mnemonic=instruction_info.mnemonic,
        encoding=instruction_info.encoding,
        reg=GLOBAL_REGISTER_NAMES[data[0] - instruction_info.opcode],
    )

    # Handle immediate value for OI encoding (like MOV reg, imm32)
    if instruction_info.encoding == ENCODINGS.OI:
        instruction_size += instruction_info.imm_size
        imm = int.from_bytes(data[1:instruction_size], byteorder="little", signed=False)
        instruction.immediate = f"0x{imm:08X}"

    return instruction, instruction_size


# Disassemble a single instruction from a stream of binary data
def disassemble(data: bytes, offset: int) -> Tuple["Instruction", int]:

    # Determine the opcode and get corresponding instruction information

    # Check for single-byte opcode
    if data[0] in GLOBAL_INSTRUCTIONS_MAP:
        opcode_size = 1
        instruction_info = GLOBAL_INSTRUCTIONS_MAP[data[0]]

    # Check for two-byte opcode (like 0F xx)
    elif int.from_bytes(data[:2], "big") in GLOBAL_INSTRUCTIONS_MAP:
        opcode_size = 2
        instruction_info = GLOBAL_INSTRUCTIONS_MAP[int.from_bytes(data[:2], "big")]

    # Check for opcode that encodes register (like 40-47 for INC)
    elif regadd_check_opcode(data[0]):
        instruction_info = regadd_check_opcode(data[0])

    # Invalid/unknown opcode - treat as data byte
    else:
        return Instruction(immediate=data[0], is_db=True), 1

    # Try to disassemble using the instruction info
    try:
        # Handle instructions with ModR/M byte
        if instruction_info.has_modrm:
            instruction, instruction_size = modrm_disassemble(
                data[opcode_size:], opcode_size, instruction_info
            )

        # Handle instructions that encode register in opcode
        elif (
            instruction_info.encoding == ENCODINGS.O
            or instruction_info.encoding == ENCODINGS.OI
        ):
            instruction, instruction_size = regadd_disassemble(data, instruction_info)

        # Handle all other instruction types
        else:
            instruction, instruction_size = no_modrm_no_regadd_disassemble(
                data[opcode_size:], opcode_size, instruction_info, offset
            )

        return instruction, instruction_size

    # If disassembly fails, treat as data byte
    except Exception as e:
        return Instruction(immediate=data[0], is_db=True), 1


# Linear sweep disassembly algorithm - disassemble all bytes sequentially
def linear_sweep(
    filename: str,
) -> Tuple[Dict[int, Tuple["Instruction", bytes]], Dict[int, str]]:
    counter = 0
    output_list = {}  # Maps offset -> (instruction, raw bytes)
    labels = {}       # Maps target address -> label name (for jumps/calls)

    # Read binary data from file
    data = get_file(filename)

    # Process each instruction sequentially
    while counter < len(data):
        original_offset = counter

        # Disassemble the current instruction
        instruction, instruction_size = disassemble(data[counter:], original_offset)

        # Generate labels for jump/call targets
        if instruction.encoding == ENCODINGS.D:
            dest_addr = instruction.immediate  # Target address
            dest_addr_str = f"{dest_addr:08X}"  # Format as hex string
            dest_label = f"offset_{dest_addr_str}h"  # Create label name
            labels[dest_addr] = dest_label  # Store in labels dictionary
            instruction.immediate = dest_label  # Replace immediate with label name

        # Store the instruction and its raw bytes in the output list
        instruction_bytes = data[original_offset : original_offset + instruction_size]
        output_list[original_offset] = (instruction, instruction_bytes)

        # Move to the next instruction
        counter += instruction_size

    return output_list, labels
