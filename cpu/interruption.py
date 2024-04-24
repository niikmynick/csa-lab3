from enum import Enum


class InterruptionType(Enum):
    INPUT = 0
    OUTPUT = 1
    HALT = 2
    ERROR = 3


class Interruption:
    def __init__(self, interruption_type: InterruptionType, message: str = ''):
        self.interruption_type = interruption_type
        self.message = message

    def __str__(self):
        return f"Interruption: {self.interruption_type.name}" + (" " if self.message != "" else "" + f"{self.message}")

    def __repr__(self):
        return str(self)
