from sys import argv
from .frontends.bf import Bf

if __name__ == "__main__":
    if len(argv) != 3:
        quit("Exactly two args are required: path to input file and path to output file.")
    input_path, output_path = argv[1:]
    Bf.file_to_asm_file(input_path, output_path)
