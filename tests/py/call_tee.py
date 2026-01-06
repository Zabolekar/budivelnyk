from sys import argv
from budivelnyk import tape_of_size, shared_to_function

libtee = shared_to_function(argv[1])
buffer = tape_of_size(1)
libtee(buffer)
