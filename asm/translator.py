from asm.instruction import Instruction, OpCode, OpType, DataType


class Translator:
    def __init__(self):
        self.DATA_SECTION_MARKER = 0xFF
        self.CODE_SECTION_MARKER = 0xFE

    @staticmethod
    def asm_to_variables(variables: dict) -> bytes:
        binary_code = b""

        for variable in variables.values():
            block = variable["address"].to_bytes(1, "big")
            block += variable["size"].to_bytes(1, "big")

            if variable["type"] == "string":
                block += DataType.STRING.value.to_bytes(1, "big")
                block += variable["init_value"].encode("utf-8")

            else:
                block += DataType.INT.value.to_bytes(1, "big")
                block += variable["init_value"].to_bytes(variable["size"], "big")

            block += b"\0"

            binary_code += block

        return binary_code

    @staticmethod
    def asm_to_instructions(instructions: list[Instruction]) -> bytes:
        binary_code = b""

        for instruction in instructions:
            # total 8 bytes for each instruction
            if instruction.operand is not None:
                block = instruction.opcode.value.to_bytes(1, "big")
                block += instruction.operand_type.value.to_bytes(1, "big")
                block += instruction.operand.to_bytes(6, "big")

            else:
                block = instruction.opcode.value.to_bytes(1, "big")
                block += instruction.operand_type.value.to_bytes(1, "big")
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

    @staticmethod
    def binary_to_variables(binary: bytes) -> dict:
        variables = {}
        i = 0

        while i < len(binary):
            address = binary[i]
            size = binary[i + 1]
            data_type = binary[i + 2]
            init_value = int.from_bytes(binary[i + 3:i + 3 + size], "big")

            variables[address] = {"init_value": init_value, "address": address, "size": size}

            i += 3 + size + 1

        return variables

    @staticmethod
    def binary_to_instructions(binary: bytes) -> dict[int, Instruction]:
        instructions = {}
        i = 0

        while i < len(binary):
            opcode = OpCode(binary[i])
            operand_type = OpType(binary[i + 1])
            operand = int.from_bytes(binary[i + 2:i + 8], "big")

            if operand_type == OpType.NOPE:
                instructions[len(instructions)] = Instruction(opcode, None, operand_type)

            else:
                instructions[len(instructions)] = Instruction(opcode, operand, operand_type)

            i += 8 + 1

        return instructions

    def binary_to_asm(self, binary: bytes) -> list[dict]:
        data_flag = False
        data_bytes = b""
        code_bytes = b""

        for byte in binary:
            if byte == self.DATA_SECTION_MARKER:
                data_flag = True
                continue

            if byte == self.CODE_SECTION_MARKER:
                data_flag = False
                continue

            if data_flag:
                data_bytes += bytes([byte])
            else:
                code_bytes += bytes([byte])

        data = self.binary_to_variables(data_bytes)
        code = self.binary_to_instructions(code_bytes)

        return [data, code]
