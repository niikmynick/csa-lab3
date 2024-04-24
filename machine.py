from memory.memory import Memory
from io_managers.input_manager import InputManager
from io_managers.output_manager import OutputManager
from io_managers.logger import Logger
from cpu.control_unit import ControlUnit
from cpu.loader import Loader


class Machine:
    def __init__(self):
        self.processor = ControlUnit()
        self.loader = Loader()

        self.instruction_memory = Memory()
        self.data_memory = Memory()

        self.input_manager = InputManager()
        self.output_manager = OutputManager()
        self.logger = Logger()

    def configure(self, bin_file: str, input_file: str, out_file: str, log_file: str):
        self.logger.set_log_filepath(log_file)

        self.input_manager.set_logger(self.logger)
        self.output_manager.set_logger(self.logger)

        self.input_manager.set_input_device(input_file)

        self.output_manager.set_terminal('stdout')
        self.output_manager.set_result_filepath(out_file)

        input_address = self.data_memory.allocate(1)
        self.data_memory.write(input_address, self.input_manager)

        output_address = self.data_memory.allocate(1)
        self.data_memory.write(output_address, self.output_manager)

        base_pointer = self.data_memory.get_last_allocated()

        self.processor.set_logger(self.logger)

        self.processor.connect_instructions_memory(self.instruction_memory)
        self.processor.connect_data_memory(self.data_memory)

        self.loader.connect_instructions_memory(self.instruction_memory)
        self.loader.connect_data_memory(self.data_memory)

        self.processor.set_base_pointer(base_pointer)
        self.processor.set_input_address(input_address)
        self.processor.set_output_address(output_address)

        self.loader.load(bin_file)

    def run(self):
        self.processor.run()
        self.input_manager.turn_off()
        self.output_manager.turn_off()
        self.logger.turn_off()
