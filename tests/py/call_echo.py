from sys import argv
from ctypes import CDLL, create_string_buffer

libecho = CDLL(argv[1])
buffer = create_string_buffer(1)
libecho.run(buffer)
