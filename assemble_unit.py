from sys import argv

from asm.assembler import Assembler


if __name__ == '__main__':
    assert len(argv) == 3, "Usage: <source_filepath> <target_filepath>"
    source = argv[1]
    target = argv[2]

    assembler = Assembler()

    assembler.assemble(source, target)
