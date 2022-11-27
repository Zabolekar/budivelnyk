from sys import argv
from ctypes import CDLL, create_string_buffer

libreads = CDLL(argv[1])
buffer = create_string_buffer(1)
libreads.run(buffer)
assert bytes(buffer) == b"c"
