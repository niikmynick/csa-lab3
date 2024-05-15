from enum import Enum


class OpCode(int, Enum):
    POP = 0x01
    COMPARE = 0x02
    DUPLICATE = 0x03
    RETURN = 0x04

    ADD = 0x05
    SUB = 0x06
    MUL = 0x07
    DIV = 0x08
    INC = 0x09
    DEC = 0x10

    SWAP = 0x11

    READ = 0x12
    SAVE = 0x13
    PUSH = 0x14

    JUMP = 0x15
    JLA = 0x16
    JLE = 0x17
    JEQ = 0x18
    JNE = 0x19

    HALT = 0x20

    NOP = 0x30

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)


class OpType(int, Enum):
    ADDRESS = 0x01
    VALUE = 0x02
    NOPE = 0x03


class DataType(int, Enum):
    INT = 0x01
    CHAR = 0x02
    STRING = 0x03
    NOPE = 0x04


class Instruction:
    def __init__(self, opcode: OpCode, operand: int | None = None, operand_type: OpType = OpType.NOPE, data_type: DataType = DataType.NOPE):
        self.opcode = opcode
        self.operand = operand
        self.operand_type = operand_type
        self.data_type = data_type

    def __str__(self):
        match self.operand_type:
            case OpType.VALUE:
                return f"{self.opcode.name} {self.operand} - {hex(self.opcode)[2:]}{hex(self.operand_type)[2:]}{hex(self.operand)[2:]}"
            case OpType.ADDRESS:
                return f"{self.opcode.name} ${self.operand} - {hex(self.opcode)[2:]}{hex(self.operand_type)[2:]}{hex(self.operand)[2:]}"
            case OpType.NOPE:
                return f"{self.opcode.name} - {hex(self.opcode)[2:]}{hex(self.operand_type)[2:]}"

    def __repr__(self):
        return str(self)


def get_opcode_by_name(name: str) -> OpCode:
    for op in OpCode:
        if op.name.lower() == name.lower():
            return op
    return OpCode.NOP


if __name__ == "__main__":
    print(Instruction(opcode=OpCode.PUSH, operand=0x01, operand_type=OpType.VALUE))
    print(Instruction(opcode=OpCode.PUSH, operand=0x01, operand_type=OpType.ADDRESS))
    print(Instruction(opcode=OpCode.PUSH, operand=None, operand_type=OpType.NOPE))
