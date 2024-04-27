from memory.memory import Memory
from asm.instruction import Instruction, OpCode, OpType, DataType


class Loader:
    def __init__(self):
        self.instructions_memory = None
        self.data_memory = None
        self.DATA_SECTION_MARKER = 0xFF
        self.CODE_SECTION_MARKER = 0xFE

    def connect_instructions_memory(self, instruction_memory: Memory):
        self.instructions_memory = instruction_memory

    def connect_data_memory(self, data_memory: Memory):
        self.data_memory = data_memory

    def load(self, filename: str):
        data_flag = False
        variables = {}

        with open(filename, 'rb') as file:
            binary_code = file.read()

            i = 0
            while i < len(binary_code):
                if binary_code[i] == self.DATA_SECTION_MARKER:
                    data_flag = True
                    i += 1
                    continue

                if binary_code[i] == self.CODE_SECTION_MARKER:
                    data_flag = False
                    i += 1
                    continue

                if data_flag:
                    address = binary_code[i]
                    size = binary_code[i + 1]
                    data_type = binary_code[i + 2]

                    # allocated_address = self.data_memory.allocate(size)

                    if data_type == DataType.STRING.value:
                        str_value = binary_code[i + 3:i + 3 + size].decode('utf-8')
                        allocated_address = self.data_memory.allocate(len(str_value) + 1)
                        c = 0
                        for j in str_value:
                            self.data_memory.write(c + allocated_address, ord(j))
                            c += 1

                        self.data_memory.write(c + allocated_address, ord('\0'))

                    else:
                        allocated_address = self.data_memory.allocate(1)
                        int_value = int.from_bytes(binary_code[i + 3:i + 3 + size], byteorder='big')
                        self.data_memory.write(allocated_address, int_value)

                    variables[address] = {
                        "actual_address": allocated_address,
                        "data_type": data_type
                    }

                    i += 3 + size + 1

                else:
                    opcode = binary_code[i]
                    operand_type = binary_code[i + 1]
                    operand = int.from_bytes(binary_code[i + 2:i + 8], "big")

                    allocated_address = self.instructions_memory.allocate(1)
                    match operand_type:
                        case OpType.NOPE.value:
                            self.instructions_memory.write(
                                allocated_address,
                                Instruction(opcode=OpCode(opcode)))
                        case OpType.VALUE.value:
                            self.instructions_memory.write(
                                allocated_address,
                                Instruction(opcode=OpCode(opcode),
                                            operand=operand,
                                            operand_type=OpType(operand_type),
                                            data_type=DataType.INT))
                        case OpType.ADDRESS.value:
                            if operand in variables and opcode not in [OpCode.JUMP.value, OpCode.JEQ.value, OpCode.JNE.value, OpCode.JLA.value, OpCode.JLE.value]:
                                temp = variables[operand]
                                self.instructions_memory.write(
                                    allocated_address,
                                    Instruction(opcode=OpCode(opcode),
                                                operand=temp["actual_address"],
                                                operand_type=OpType(operand_type),
                                                data_type=DataType(temp["data_type"])))
                            else:
                                self.instructions_memory.write(
                                    allocated_address,
                                    Instruction(opcode=OpCode(opcode),
                                                operand=operand,
                                                operand_type=OpType(operand_type),
                                                data_type=DataType.INT))

                    i += 8 + 1
