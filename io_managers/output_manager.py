from io_managers.logger import Logger, LogLevel, Place
from sys import stdout


class OutputManager:
    def __init__(self):
        self.terminal = None
        self.output_device = None
        self.logger = None

    def set_logger(self, logger: Logger):
        self.logger = logger

    def set_terminal(self, terminal: str):
        if terminal == 'stdout':
            self.terminal = stdout
            # self.logger.log(LogLevel.INFO, Place.OUTPUT, "Using stdout as terminal.")
        else:
            try:
                self.terminal = open(terminal, 'w')
                # self.logger.log(LogLevel.INFO, Place.OUTPUT, "Using " + terminal + " as terminal.")
            except FileNotFoundError:
                # self.logger.log(LogLevel.ERROR, Place.OUTPUT, "File not found. Using stdout as terminal.")
                self.terminal = stdout

    def set_result_filepath(self, result_filepath: str):
        try:
            self.output_device = open(result_filepath, 'w')
            # self.logger.log(LogLevel.INFO, Place.OUTPUT, "Using " + result_filepath + " as result file.")
        except FileNotFoundError:
            # self.logger.log(LogLevel.ERROR, Place.OUTPUT, "Result file not found")
            exit(1)

    def write(self, data: str):
        self.write_terminal(data)
        self.write_file(data)

    def write_terminal(self, data: str):
        self.terminal.write(data)
        self.terminal.flush()

    def write_file(self, data: str):
        if self.output_device is not None:
            self.output_device.write(data)
            self.output_device.flush()

    def turn_off(self):
        if self.output_device is not None:
            self.logger.log(LogLevel.INFO, Place.OUTPUT, "Turning off output device.")
            self.output_device.close()

    def __str__(self):
        return "OutputManager"

    def __repr__(self):
        return str(self)
