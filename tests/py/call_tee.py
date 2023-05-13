from sys import argv
from ctypes import CDLL
from budivelnyk import make_tape

libtee = CDLL(argv[1])
buffer = make_tape(1)
libtee.run(buffer)
