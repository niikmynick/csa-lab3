from asm.instruction import Instruction, OpCode, OpType, DataType


class Translator:
    def __init__(self):
        self.INTERRUPTION_MARKER = 0xFF
        self.DATA_SECTION_MARKER = 0xFE
        self.CODE_SECTION_MARKER = 0xFD

    @staticmethod
    def asm_to_variables(variables: dict) -> bytes:
        binary_code = b""

        for variable in variables.values():
            block = variable["address"].to_bytes(1, "big", signed=True)
            block += variable["size"].to_bytes(1, "big", signed=True)

            if variable["type"] == "string":
                block += DataType.STRING.value.to_bytes(1, "big", signed=True)
                block += variable["init_value"].encode("utf-8")

            else:
                block += DataType.INT.value.to_bytes(1, "big", signed=True)
                block += variable["init_value"].to_bytes(variable["size"], "big", signed=True)

            block += b"\0"

            binary_code += block

        return binary_code

    @staticmethod
    def asm_to_instructions(instructions: list[Instruction]) -> bytes:
        binary_code = b""

        for instruction in instructions:
            # total 8 bytes for each instruction
            if instruction.operand is not None:
                block = instruction.opcode.value.to_bytes(1, "big", signed=True)
                block += instruction.operand_type.value.to_bytes(1, "big", signed=True)
                block += instruction.operand.to_bytes(6, "big", signed=True)

            else:
                block = instruction.opcode.value.to_bytes(1, "big", signed=True)
                block += instruction.operand_type.value.to_bytes(1, "big", signed=True)
                block += b"\0\0\0\0\0\0"

            block += b"\0"

            binary_code += block

        return binary_code

    def asm_to_binary(self, variables: dict, instructions: list[Instruction]) -> bytes:
        binary_code = b""

        binary_code += self.DATA_SECTION_MARKER.to_bytes(1, "big")

        binary_code += self.asm_to_variables(variables)

        binary_code += self.CODE_SECTION_MARKER.to_bytes(1, "big")

        binary_code += self.asm_to_instructions(instructions)

        return binary_code

    def binary_to_asm(self, binary: bytes) -> list[dict]:
        data = {}
        code: dict[int, Instruction] = {}

        data_flag = False

        i = 0
        while i < len(binary):
            if binary[i] == self.DATA_SECTION_MARKER:
                data_flag = True
                i += 1
                continue

            if binary[i] == self.CODE_SECTION_MARKER:
                data_flag = False
                i += 1
                continue

            if binary[i] == self.INTERRUPTION_MARKER:
                data_flag = False
                i += 2
                continue

            if data_flag:
                address = binary[i]
                size = binary[i + 1]
                data_type = binary[i + 2]

                if data_type == DataType.STRING.value:
                    str_value = binary[i + 3:i + 3 + size].decode('utf-8')
                    data[address] = str_value

                else:
                    int_value = int.from_bytes(binary[i + 3:i + 3 + size], byteorder='big', signed=True)
                    data[address] = str(int_value)

                i += 3 + size + 1

            else:
                opcode = binary[i]
                operand_type = binary[i + 1]
                operand = int.from_bytes(binary[i + 2:i + 8], "big", signed=True)

                match operand_type:
                    case OpType.NOPE.value:
                        code[len(code)] = Instruction(opcode=OpCode(opcode))
                    case OpType.VALUE.value:
                        code[len(code)] = Instruction(opcode=OpCode(opcode),
                                                      operand=operand,
                                                      operand_type=OpType(operand_type),
                                                      data_type=DataType.INT)
                    case OpType.ADDRESS.value:
                        code[len(code)] = Instruction(opcode=OpCode(opcode),
                                                      operand=operand,
                                                      operand_type=OpType(operand_type),
                                                      data_type=DataType.INT)

                i += 8 + 1

        return [data, code]
