from sys import argv
import budivelnyk as bd

libhello = bd.shared_to_function(argv[1])
buffer = bd.tape_of_size(3)
libhello(buffer)
