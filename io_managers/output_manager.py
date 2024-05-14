from io_managers.logger import Logger, LogLevel, Place


class OutputManager:
    def __init__(self):
        self.output_device = None
        self.logger = None

    def set_logger(self, logger: Logger):
        self.logger = logger

    def set_result_filepath(self, result_filepath: str):
        try:
            self.output_device = open(result_filepath, 'w')
        except FileNotFoundError:
            exit(1)

    def write(self, data):
        self.output_device.write(chr(data))
        self.output_device.flush()

    def turn_off(self):
        self.logger.log(LogLevel.INFO, Place.OUTPUT, "Turning off output device.")
        self.output_device.close()

    def __str__(self):
        return "OutputManager"

    def __repr__(self):
        return str(self)
