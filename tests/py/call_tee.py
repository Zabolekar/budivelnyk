from sys import argv
from ctypes import CDLL
from budivelnyk import create_tape

libtee = CDLL(argv[1])
buffer = create_tape(1)
libtee.run(buffer)
