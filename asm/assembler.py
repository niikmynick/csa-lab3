from asm.translator import Translator
from asm.instruction import Instruction, OpType, get_opcode_by_name


class Assembler:
    def __init__(self):
        self.translator = Translator()

        self.all_instructions = ["push", "pop", "read", "write", "compare", "jump", "jla", "jle", "jeq", "jne", "add", "sub", "mul", "div", "inc", "dec", "save", "halt"]
        self.no_op_instructions = ["pop", "read", "write", "compare", "add", "sub", "mul", "div", "inc", "dec", "halt"]
        self.one_op_instructions = ["push", "jump", "jne", "jeq", "jla", "jle", "save"]
        self.jump_instructions = ["jump", "jne", "jeq", "jla", "jle"]

    def assemble(self, code_file: str, binary_file: str):
        with open(code_file, "r") as file:
            code = file.read()

        lines = code.strip().split("\n")
        lines = list(map(str.strip, lines))
        lines = list(filter(lambda x: x != "", lines))
        lines = list(filter(lambda x: x[0] != "#", lines))

        assert ".code" in lines, "No code section found"

        labels = {}
        # variables = { "name": { "init_value": 0, "type": "int", "address": 0, "size": 0 }, }
        variables: dict[str, dict[str, int | str]] = {}
        instructions = []

        data_flag = False
        instructions_counter = 0
        memory_counter = 0

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

                assert elements[0] not in self.all_instructions, f"Var {elements[0]} has the same name as an instruction"
                assert not elements[0].isnumeric(), f"Variable name {elements[0]} is a number"
                assert not elements[0][0].isdigit(), f"Variable name {elements[0]} starts with a digit"

                assert elements[1].isnumeric() or elements[1].startswith('"') or elements[1].startswith("'"), f"Value for var {elements[0]} is not a number or a string"

                if "'" in elements[1]:
                    assert elements[1].startswith("'") and elements[1].endswith("'"), f"Value for var {elements[0]} is not enclosed in single quotes"

                elif '"' in elements[1]:
                    assert elements[1].startswith('"') and elements[1].endswith('"'), f"Value for var {elements[0]} is not enclosed in double quotes"

            elif line.endswith(":"):
                label = line[:-1]
                assert not label.isnumeric(), f"Label {label} is a number"
                assert not label[0].isdigit(), f"Label {label} starts with a digit"
                assert label not in self.all_instructions, f"Label {label} has the same name as an instruction"
                assert label not in labels, f"Label {label} is already defined"
                assert label not in variables.keys(), f"Label {label} is already defined as a variable"

            else:
                elements = line.split(" ", 1)

                assert elements[0] in self.all_instructions, f"Unknown instruction {elements[0]}"

                if elements[0] in self.no_op_instructions:
                    assert len(elements) == 1, f"Instruction {elements[0]} does not take any operands"

                elif elements[0] in self.one_op_instructions:
                    assert len(elements) == 2, f"Instruction {elements[0]} takes exactly one operand"

                    operand = elements[1]

                    assert operand.isnumeric() or operand.startswith('"') or operand.startswith("'") or elements, f"Operand {operand} for instruction {elements[0]} is not a number or a string"

                    if "'" in operand:
                        assert operand.startswith("'") and operand.endswith("'"), f"Operand {operand} for instruction {elements[0]} is not enclosed in single quotes"

                    elif '"' in operand:
                        assert operand.startswith('"') and operand.endswith('"'), f"Operand {operand} for instruction {elements[0]} is not enclosed in double quotes"

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
                    init_value = int(arg)
                    size = len(hex(init_value)) - 2
                    arg_type = "int"

                else:
                    init_value = arg[1:-1]
                    if "\\n" in init_value:
                        size = len(init_value) - 1
                        init_value = init_value.replace("\\n", "\n")
                    size = len(init_value)
                    arg_type = "string"

                value = {"init_value": init_value, "type": arg_type, "address": memory_counter, "size": size}
                variables[name] = value

                memory_counter += size

                continue

            if line.endswith(":"):
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
                elements = line.split(" ", 1)
                opcode = get_opcode_by_name(elements[0])
                optype = OpType.VALUE

                if len(elements) == 1:
                    operand = None
                    optype = OpType.NOPE

                elif elements[1] in variables:
                    operand = variables[elements[1]]["address"]
                    optype = OpType.ADDRESS

                elif elements[1] in labels:
                    assert elements[0] in self.jump_instructions, f"Label {elements[1]} is not allowed in instruction {elements[0]}"
                    operand = labels[elements[1]]
                    optype = OpType.ADDRESS

                elif elements[1].isnumeric():
                    operand = int(elements[1])

                elif "'" in elements[1] or '"' in elements[1]:
                    operand = elements[1][1:-1]

                else:
                    operand = elements[1]

                instructions.append(Instruction(opcode, operand, optype))

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

        binary = self.translator.asm_to_binary(variables, instructions)

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
    assembler.assemble("test.asm", "test.bin")
    assembler.disassemble("test.bin", "test_dis.asm")
