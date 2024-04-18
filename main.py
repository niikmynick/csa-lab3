from memory.memory import Memory
from io_managers.input_manager import InputManager
from io_managers.output_manager import OutputManager
from cpu.control_unit import ControlUnit
from cpu.loader import Loader
from asm.assembler import Assembler


def main():
    # init memory
    instruction_memory = Memory()
    data_memory = Memory()

    # init io managers
    input_manager = InputManager()
    output_manager = OutputManager('test.txt', 'test.log')

    # add io managers to data memory
    input_address = data_memory.allocate(1)
    data_memory.write(input_address, input_manager)

    output_address = data_memory.allocate(1)
    data_memory.write(output_address, output_manager)

    # init loader
    loader = Loader(instruction_memory, data_memory)

    # init assembler
    assembler = Assembler()

    # assemble and load program
    assembler.assemble("test.asm", "test.bin")
    # assembler.disassemble("test.bin", "test_dis.asm")

    base_pointer = data_memory.get_last_allocated()
    loader.load("test.bin")

    # init processor
    processor = ControlUnit(instruction_memory, data_memory, input_address, output_address, base_pointer)

    # run processor
    processor.run()


if __name__ == '__main__':
    main()
