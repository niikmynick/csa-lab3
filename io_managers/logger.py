from io_managers.output_manager import OutputManager


class Logger:
    def __init__(self, output_manager: OutputManager):
        self.output_manager = output_manager

    def log(self, data: str):
        self.output_manager.log(data + '\n')
