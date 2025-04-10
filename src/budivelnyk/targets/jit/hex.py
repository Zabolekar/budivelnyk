def from_hex(s: str) -> bytes:
    tokens = s.split()
    return bytes(int(n, 16) for n in tokens)


# because b("80 2F", n) is easier to read than b"\x80\x2f%c" % n
def b(hex_opcode: str, constant: int|bytes|None = None) -> bytes:
    opcode = from_hex(hex_opcode)

    match constant:
        case None:
            return opcode
        case bytes():
            return opcode + constant
        case int():
            return opcode + bytes([constant])
