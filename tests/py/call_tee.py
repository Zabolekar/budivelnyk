from sys import argv
from ctypes import CDLL
from budivelnyk import tape_of_size

libtee = CDLL(argv[1])
buffer = tape_of_size(1)
libtee.run(buffer)
