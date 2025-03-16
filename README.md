# x86 Disassembler

## Overview

This project is an x86 instruction set disassembler that converts binary machine code into human-readable assembly language. It focuses on 32-bit x86 instructions and implements a linear sweep disassembly algorithm to process binary files. The disassembler supports a wide range of common x86 instructions including arithmetic operations, control flow, memory access, and stack manipulation. 

*Note that this implementation covers approximately 10% of the full x86 instruction set, focusing on the most commonly used instructions.*
    
## How to Use

### Requirements
- Python 3.6 or higher

### Installation
No additional packages are required. Simply clone the repository.

### Usage
Run the disassembler by providing a binary file to analyze:

```bash
python main.py -i <input_binary_file>
```

Example:
```bash
python main.py -i sample-inputs/example1
```

The disassembler will output the assembly code to the console, showing:
- Memory offsets
- Hexadecimal representation of machine code bytes
- Disassembled instructions
- Labels for jump and call targets

## How It Works

The disassembler uses a **linear sweep** algorithm, which processes the binary file sequentially from start to finish:

1. **Binary Loading**: The binary file is loaded into memory as a byte array.
2. **Sequential Processing**: The algorithm processes each instruction in sequence, starting from the first byte.
3. **Instruction Decoding**: Each instruction is decoded based on the x86 instruction format:
   - Opcode identification
   - ModR/M byte parsing (if present)
   - SIB byte parsing (if present)
   - Displacement and immediate value extraction
4. **Operand Resolution**: Register and memory operands are resolved based on the ModR/M and SIB bytes.
5. **Label Generation**: Jump and call targets are identified and labeled for better readability.
6. **Output Formatting**: Instructions are formatted with their memory offsets and raw bytes.

The linear sweep approach is straightforward but may incorrectly interpret data as code if data is embedded within the code section. However, it provides a good baseline for disassembly and works well for most compiled code.

## Supported Instructions

The disassembler supports the following x86 instructions:

### Arithmetic and Logic
- `add` - Addition
- `and` - Logical AND
- `cmp` - Compare
- `dec` - Decrement
- `inc` - Increment
- `or` - Logical OR
- `sub` - Subtraction
- `test` - Logical comparison
- `xor` - Logical XOR
- `idiv` - Integer division
- `not` - Bitwise NOT

### Data Movement
- `mov` - Move data
- `lea` - Load effective address
- `movsd` - Move string doubleword
- `push` - Push onto stack
- `pop` - Pop from stack

### Control Flow
- `call` - Call procedure
- `jmp` - Unconditional jump
- `jz` - Jump if zero
- `jnz` - Jump if not zero
- `retn` - Return from near procedure
- `retf` - Return from far procedure

### String Operations
- `movsd` - Move string doubleword
- `repne cmpsd` - Repeat string comparison

### Miscellaneous
- `nop` - No operation
- `clflush` - Flush cache line

Each instruction supports various addressing modes and operand types as defined in the x86 architecture, including:
- Register operands
- Memory operands with various addressing modes
- Immediate values
- Relative displacements for jumps and calls

The disassembler handles complex addressing modes including SIB (Scale-Index-Base) addressing and various displacement sizes.

