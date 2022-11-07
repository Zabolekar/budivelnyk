from sys import argv
from ctypes import CDLL

libhello = CDLL(argv[1])
buffer = bytes(3)
libhello.run(buffer)
