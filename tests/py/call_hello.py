from sys import argv
from ctypes import CDLL, create_string_buffer

libhello = CDLL(argv[1])
buffer = create_string_buffer(3)
libhello.run(buffer)
