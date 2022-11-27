from sys import argv
from ctypes import CDLL

libreads = CDLL(argv[1])
buffer = bytes(1)
libreads.run(buffer)
assert buffer == b"c"
