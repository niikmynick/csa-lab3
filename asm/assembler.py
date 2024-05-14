from asm.translator import Translator
from asm.instruction import Instruction, OpCode, OpType, get_opcode_by_name


class Assembler:
    def __init__(self):
        self.translator = Translator()

        self.all_instructions = [code.name.lower() for code in OpCode]
        self.no_op_instructions = [code.name.lower() for code in OpCode if (code.value <= 0x11 or code.value == 0x20)]
        self.one_op_instructions = [code.name.lower() for code in OpCode if 0x14 <= code.value < 0x20]
        self.jump_instructions = ["jump", "jne", "jeq", "jla", "jle"]
        self.system_variables = {"INPUT": 0, "OUTPUT": 1, "EXTRA": 2}

    def assemble(self, code_file: str, binary_file: str):
        lines = []
        with open(code_file, "r") as file:
            code = file.readlines()
            for line in code:
                line = line.strip()

                if line == "" or line.startswith("#"):
                    continue

                lines.append(line.strip())

        assert ".code" in lines, "No code section found"

        labels: dict[str, int] = {}
        # variables = { "name": { "init_value": 0, "type": "int", "address": 0, "size": 0 }, ... }
        variables: dict[str, dict[str, int | str]] = {}
        instructions = []

        data_flag = False
        instructions_counter = 0
        memory_counter = 3

        # syntax check
        for line in lines:
            if line == ".data":
                data_flag = True
                continue

            elif line == ".code":
                data_flag = False
                continue

            if data_flag:
                elements = line.split(" ", 1)

                assert len(elements) == 2, f"No value provided for var {elements[0]}"

                assert elements[0] not in self.all_instructions, \
                    f"Var {elements[0]} has the same name as an instruction"
                assert not elements[0].isnumeric(), f"Variable name {elements[0]} is a number"
                assert not elements[0][0].isdigit(), f"Variable name {elements[0]} starts with a digit"

                assert elements[0] not in self.system_variables.keys(), \
                    f"Var {elements[0]} shadows a system var"

                assert elements[1].isnumeric() or elements[1].startswith('"') or elements[1].startswith("'"), \
                    f"Value for var {elements[0]} is not a number or a string"

                if "'" in elements[1]:
                    assert elements[1].startswith("'") and elements[1].endswith("'"), \
                        f"Value for var {elements[0]} is not enclosed in single quotes"

                elif '"' in elements[1]:
                    assert elements[1].startswith('"') and elements[1].endswith('"'), \
                        f"Value for var {elements[0]} is not enclosed in double quotes"

            elif line.endswith(":"):
                label = line[:-1]
                assert not label.isnumeric(), f"Label {label} is a number"
                assert not label[0].isdigit(), f"Label {label} starts with a digit"
                assert label not in self.all_instructions, f"Label {label} has the same name as an instruction"
                assert label not in labels, f"Label {label} is already defined"
                assert label not in variables.keys(), f"Label {label} is already defined as a variable"

            else:
                elements = line.split(" ", 1)
                operation: str = elements[0].lower()

                assert operation in self.all_instructions, f"Unknown instruction {operation}"

                if operation in self.no_op_instructions:
                    assert len(elements) == 1, f"Instruction {operation} does not take any operands"

                elif operation in self.one_op_instructions:
                    assert len(elements) == 2, f"Instruction {operation} takes exactly one operand"

                    operand: str = elements[1]

                    assert ' ' not in operand, f"Operand {operand} contains spaces"
                    assert '"' not in operand, f"Operand {operand} contains double quotes"
                    assert "'" not in operand, f"Operand {operand} contains single quotes"

        # parse variables and labels
        for line in lines:
            if line == ".data":
                data_flag = True
                continue

            elif line == ".code":
                data_flag = False
                continue

            if data_flag:
                elements = line.split(" ", 1)
                name, arg = elements

                if arg.isnumeric():
                    int_value = int(arg)
                    size = len(hex(int_value)) - 2
                    arg_type = "int"
                    int_arg_value: dict[str, int | str] = {
                        "init_value": int_value,
                        "type": arg_type,
                        "address": memory_counter,
                        "size": size
                    }

                    variables[name] = int_arg_value

                else:
                    str_value = arg[1:-1]
                    str_value = str_value.replace("\\n", "\n")
                    size = len(str_value)
                    arg_type = "string"
                    str_arg_value: dict[str, int | str] = {
                        "init_value": str_value,
                        "type": arg_type,
                        "address": memory_counter,
                        "size": size
                    }

                    variables[name] = str_arg_value

                memory_counter += size

                continue

            elif line.endswith(":"):
                label = line[:-1]
                labels[label] = instructions_counter
                continue

            instructions_counter += 1

        # parse tokens
        for line in lines:
            if line == ".data":
                data_flag = True
                continue

            elif line == ".code":
                data_flag = False
                continue

            if data_flag:
                continue

            elif line.endswith(":"):
                continue

            else:
                instruction_elements: list[str] = line.split(" ", 1)
                opcode: OpCode = get_opcode_by_name(instruction_elements[0])
                optype: OpType = OpType.VALUE
                instruction_operand: int

                if len(instruction_elements) == 1:
                    instructions.append(Instruction(opcode))
                    instructions_counter += 1
                    continue

                elif instruction_elements[1] in self.system_variables.keys():
                    instruction_operand = self.system_variables[instruction_elements[1]]
                    optype = OpType.ADDRESS

                elif instruction_elements[1] in variables:
                    instruction_operand = int(variables[instruction_elements[1]]["address"])
                    optype = OpType.ADDRESS

                elif instruction_elements[1] in labels:
                    assert instruction_elements[0] in self.jump_instructions, \
                        f"Label {instruction_elements[1]} is not allowed in instruction {instruction_elements[0]}"
                    assert instruction_elements[1] != "on_input", \
                        "Label 'on_input' is reserved for interruption, don't use it as an operand"
                    instruction_operand = labels[instruction_elements[1]]
                    optype = OpType.ADDRESS

                else:
                    instruction_operand = int(instruction_elements[1])

                instructions.append(Instruction(opcode, instruction_operand, optype))

                instructions_counter += 1

        # with open(code_file[:-4] + "_mid.asm", "w") as file:
        #     text = ".data\n"
        #     for variable in variables.values():
        #         text += f"{variable['address']} {variable['init_value']}\n"
        #
        #     text += f".code\n"
        #     for instruction in instructions:
        #         if instruction.operand is not None:
        #             text += f"{instruction.opcode} {instruction.operand}\n"
        #
        #         else:
        #             text += f"{instruction.opcode}\n"
        #
        #     file.write(text)

        binary = b""
        if "on_input" in labels:
            binary += 0xFF.to_bytes(1, "big")
            binary += labels["on_input"].to_bytes(1, "big")

        binary += self.translator.asm_to_binary(variables, instructions)

        with open(binary_file, "wb") as file:
            file.write(binary)

    def disassemble(self, binary_file: str, code_file: str):
        with open(binary_file, "rb") as file:
            binary = file.read()

        data, code = self.translator.binary_to_asm(binary)

        text = f".data\n"
        for address, variable in data.items():
            text += f"{address} {variable['init_value']}\n"

        text += f".code\n"
        for instruction in code.values():
            if instruction.operand is not None:
                text += f"{instruction.opcode} {instruction.operand}\n"

            else:
                text += f"{instruction.opcode}\n"

        with open(code_file, "w") as file:
            file.write(text)


if __name__ == '__main__':
    assembler = Assembler()
    # print(assembler.all_instructions)
    # print(assembler.no_op_instructions)
    # print(assembler.one_op_instructions)
    assembler.assemble("test.asm", "test.bin")
    assembler.disassemble("test.bin", "test_dis.asm")
