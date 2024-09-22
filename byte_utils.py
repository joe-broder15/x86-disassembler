# utility functions to assist with the parsing of bytes


# returns an entire file as a byte array
def get_file(filename):
    with open(filename, "rb") as f:
        a = f.read()
    return a


# parse the modrm byte
def parse_modrm(modrm):
    mod = (modrm & 0b11000000) >> 6
    reg = (modrm & 0b00111000) >> 3
    rm = modrm & 0b00000111
    return (mod, reg, rm)


# parse the sib byte
def parse_sib(sib):
    scale = (sib & 0b11000000) >> 6
    index = (sib & 0b00111000) >> 3
    base = sib & 0b00000111
    return (2**scale, index, base)


# convert an 1 byte int read from a byte array to a signed int
def to_signed(byte_value: int):
    return (byte_value - 256) if byte_value > 127 else byte_value
