from enum import Enum


class OpCode(int, Enum):
    PUSH = 0x01
    JUMP = 0x02
    JLA = 0x03
    JLE = 0x04
    JEQ = 0x05
    JNE = 0x06
    SAVE = 0x07

    POP = 0x10
    COMPARE = 0x11

    READ = 0x20
    WRITE = 0x21

    ADD = 0x31
    SUB = 0x32
    MUL = 0x33
    DIV = 0x34
    INC = 0x35
    DEC = 0x36

    HALT = 0x40

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class OpType(Enum):
    ADDRESS = 0x01
    VALUE = 0x02
    NOPE = 0x03


class DataType(Enum):
    INT = 0x01
    CHAR = 0x02
    STRING = 0x03


class Instruction:
    def __init__(self, opcode: OpCode, operand: int = None, operand_type: OpType = None, data_type: DataType = None):
        self.opcode = opcode
        self.operand = operand
        self.operand_type = operand_type
        self.data_type = data_type

    def __str__(self):
        return f"{self.opcode} {self.operand_type} {self.operand}" if self.operand is not None else f"{self.opcode}"

    def __repr__(self):
        return str(self)


def get_opcode_by_name(name: str) -> OpCode | None:
    for op in OpCode:
        if op.name.lower() == name.lower():
            return op
    return None


if __name__ == "__main__":
    print(Instruction(opcode=OpCode.PUSH, operand=0x01, operand_type=OpType.VALUE))
    print(Instruction(opcode=OpCode.PUSH, operand=0x01, operand_type=OpType.ADDRESS))
    print(Instruction(opcode=OpCode.PUSH))

    print(type(get_opcode_by_name("push")))