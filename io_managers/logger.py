from io_managers.output_manager import OutputManager
from enum import Enum


class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    DEBUG = 3


class Place(Enum):
    INTER = 0
    INSTR = 1
    ALU = 2
    SYSTEM = 3


class Logger:
    def __init__(self, output_manager: OutputManager):
        self.output_manager = output_manager

    def log(self, level: LogLevel, place: Place, message: str):
        self.output_manager.log(f"{level.name:<10}{'::':<7}{place.name:<12}{message}\n")
