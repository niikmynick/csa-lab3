from memory.memory import Memory
from io_managers.input_manager import InputManager
from io_managers.output_manager import OutputManager
from io_managers.logger import Logger
from cpu.control_unit import ControlUnit
from cpu.loader import Loader
from asm.assembler import Assembler

import datetime


def main(test_name: str):
    timestamp = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')

    code_filepath = './golden/' + test_name + '.asm'
    binary_filepath = './output/binaries/' + test_name + '.bin'

    result_filepath = './output/results/result_' + test_name + '_' + timestamp + '.txt'
    log_filepath = './output/logs/log_' + test_name + '_' + timestamp + '.log'

    # init memory
    instruction_memory = Memory()
    data_memory = Memory()

    # init io managers
    input_manager = InputManager()
    output_manager = OutputManager(result_filepath, log_filepath)
    logger = Logger(output_manager)

    # init loader
    loader = Loader(instruction_memory, data_memory)

    # init assembler
    assembler = Assembler()

    # assemble and load program
    assembler.assemble(code_filepath, binary_filepath)

    # add io managers to data memory
    input_address = data_memory.allocate(1)
    data_memory.write(input_address, input_manager)

    output_address = data_memory.allocate(1)
    data_memory.write(output_address, output_manager)

    base_pointer = data_memory.get_last_allocated()
    loader.load(binary_filepath)

    # init processor
    processor = ControlUnit(instruction_memory, data_memory, input_address, output_address, base_pointer, logger)

    # run processor
    processor.run()


if __name__ == '__main__':
    main("zero_division")
