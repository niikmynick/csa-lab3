from sys import stdin
from io_managers.logger import Logger, LogLevel, Place


class InputManager:
    def __init__(self):
        self._input = None
        self.input_device = None
        self.logger = None

    def set_input_device(self, input_device: str):
        if input_device == 'stdin':
            self.input_device = stdin
            # self.logger.log(LogLevel.INFO, Place.INPUT, 'Using stdin as input device.')
        else:
            try:
                self.input_device = open(input_device, 'r')
                temp = []
                for line in self.input_device.readlines():
                    time, value = line.strip().split(":")
                    temp.append((int(time), value))

                self.set_input(temp)
                self.logger.log(LogLevel.INFO, Place.INPUT, f'Input schedule: {temp}')

                # self.logger.log(LogLevel.INFO, Place.INPUT, 'Using ' + input_device + ' as input device.')
            except FileNotFoundError:
                # self.logger.log(LogLevel.ERROR, Place.INPUT, 'File not found. Using stdin as input device.')
                self.input_device = stdin

    def set_logger(self, logger: Logger):
        self.logger = logger

    def get_input(self):
        return self._input

    def set_input(self, arg):
        self._input = arg

    def read(self):
        if self.input_device == stdin:
            print("> ", end=" ")
            self.set_input((0, self.input_device.readline().strip()))

    def turn_off(self):
        if self.input_device is not None:
            self.logger.log(LogLevel.INFO, Place.INPUT, 'Turning off input device.')
            self.input_device.close()

    def __str__(self):
        return "InputManager"

    def __repr__(self):
        return str(self)
