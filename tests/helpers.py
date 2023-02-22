from pathlib import PosixPath


def generate_paths(tmp_path: PosixPath, name: str):
    asm = tmp_path / f"{name}.s"
    library = tmp_path / f"lib{name}.so"
    return asm, library
