from sys import argv
from ctypes import CDLL

libecho = CDLL(argv[1])
buffer = bytes(1)
libecho.run(buffer)
