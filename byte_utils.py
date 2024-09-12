def get_file(filename):
    with open(filename, "rb") as f:
        a = f.read()
    return a


def parse_modrm(modrm):
    # mod = (modrm & 0xC0) >> 6
    # reg = (modrm & 0x38) >> 3
    # rm  = (modrm & 0x07)

    mod = (modrm & 0b11000000) >> 6
    reg = (modrm & 0b00111000) >> 3
    rm = modrm & 0b00000111
    return (mod, reg, rm)


def parse_sib(sib):
    scale = (sib & 0b11000000) >> 6
    index = (sib & 0b00111000) >> 3
    base = sib & 0b00000111
    return (2**scale, index, base)
