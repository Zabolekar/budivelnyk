from sys import argv
from . import bf_to_asm

if __name__ == "__main__":
    if len(argv) != 3:
        quit("Exactly two args are required: path to input file and path to output file.")
    input_path, output_path = argv[1:]
    bf_to_asm(input_path, output_path)
