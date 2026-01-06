from sys import argv
import budivelnyk as bd

libreads = bd.shared_to_function(argv[1])
buffer = bd.tape_of_size(1)
libreads(buffer)
assert bytes(buffer) == b"c"
