from memory.memory import Memory
from io_managers.input_manager import InputManager
from io_managers.output_manager import OutputManager
from io_managers.logger import Logger
from cpu.control_unit import ControlUnit
from cpu.loader import Loader
from asm.assembler import Assembler

import datetime


def configure_io_managers(input_manager: InputManager, output_manager: OutputManager, logger: Logger, test_name: str):
    timestamp = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')

    result_filepath = './output/results/result_' + test_name + '_' + timestamp + '.txt'
    log_filepath = './output/logs/log_' + test_name + '_' + timestamp + '.txt'

    logger.set_log_filepath(log_filepath)
    input_manager.set_logger(logger)
    output_manager.set_logger(logger)

    input_manager.set_input_device("a.txt")

    output_manager.set_result_filepath(result_filepath)


def map_io_devices(data_memory: Memory, input_manager: InputManager, output_manager: OutputManager):
    input_address = data_memory.allocate(1)
    data_memory.write(input_address, input_manager)

    output_address = data_memory.allocate(1)
    data_memory.write(output_address, output_manager)


def connect_units(processor: ControlUnit, loader: Loader, instruction_memory: Memory, data_memory: Memory):
    processor.connect_instructions_memory(instruction_memory)
    processor.connect_data_memory(data_memory)

    loader.connect_instructions_memory(instruction_memory)
    loader.connect_data_memory(data_memory)

    loader.connect_control_unit(processor)


def preprocess_code(assembler: Assembler, loader: Loader, test_name: str):
    code_filepath = './golden/src/' + test_name + '.asm'
    binary_filepath = './output/binaries/' + test_name + '.bin'

    assembler.assemble(code_filepath, binary_filepath)
    loader.load(binary_filepath)


def turn_off_io_managers(input_manager: InputManager, output_manager: OutputManager, logger: Logger):
    input_manager.turn_off()
    output_manager.turn_off()
    logger.turn_off()


def main(test_name: str):
    processor = ControlUnit()
    loader = Loader()

    instruction_memory = Memory()
    data_memory = Memory()

    input_manager = InputManager()
    output_manager = OutputManager()
    logger = Logger()

    assembler = Assembler()

    configure_io_managers(input_manager, output_manager, logger, test_name)
    map_io_devices(data_memory, input_manager, output_manager)

    processor.set_logger(logger)
    processor.set_schedule([element[0] for element in input_manager.get_input()])
    connect_units(processor, loader, instruction_memory, data_memory)

    preprocess_code(assembler, loader, test_name)

    processor.run()

    turn_off_io_managers(input_manager, output_manager, logger)


if __name__ == '__main__':
    main("cat")
