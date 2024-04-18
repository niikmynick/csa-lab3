from cpu.stack import Stack
from cpu.alu import ALU
from memory.memory import Memory
from asm.instruction import Instruction, OpCode, OpType


class ControlUnit:
    def __init__(self, instruction_memory: Memory, data_memory: Memory, input_address: int, output_address: int, base_pointer: int = 0):
        self._time: int = 0
        self._instruction_counter: int = 0
        self.data_stack = Stack()
        self.instructions_stack = Stack()
        self.alu = ALU()

        self.instructions_memory = instruction_memory
        self.data_memory = data_memory

        self.input_address = input_address
        self.output_address = output_address
        self.base_pointer = base_pointer

    def tick(self):
        self._time += 1

    def get_time(self) -> int:
        return self._time

    def increment_instruction_counter(self):
        self._instruction_counter += 1

    def get_instruction_counter(self) -> int:
        return self._instruction_counter

    def handle_command(self, instruction: Instruction):
        opcode = instruction.opcode
        operand = instruction.operand
        optype = instruction.operand_type

        assert opcode in OpCode, f"Unknown opcode {opcode}"

        match opcode:
            case OpCode.PUSH:
                if optype == OpType.VALUE:
                    self.data_stack.push(operand)

                elif optype == OpType.ADDRESS:
                    value = self.data_memory.read(self.base_pointer + operand)
                    for symbol in value[::-1]:
                        self.data_stack.push(symbol)
                    # self.data_stack.push(value)

            case OpCode.POP:
                self.data_stack.pop()

            case OpCode.READ:
                self.data_memory.write(self.output_address, '> ')
                value = self.data_memory.read(self.input_address)

                self.data_stack.push(None)
                for symbol in value[::-1]:
                    self.data_stack.push(symbol)

            case OpCode.WRITE:
                while True:
                    symbol = self.data_stack.pop()
                    if symbol is None:
                        break

                    self.data_memory.write(self.output_address, symbol)

            case OpCode.COMPARE:
                #     a > b -> 1
                #     a < b -> -1
                #     a == b -> 0
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.alu.compare(a, b)

            case OpCode.JUMP:
                self.instructions_stack.push(operand)

            case OpCode.JLA:
                if not self.alu.zero and not self.alu.negative:
                    self.instructions_stack.push(operand)

            case OpCode.JLE:
                if self.alu.negative:
                    self.instructions_stack.push(operand)

            case OpCode.JEQ:
                if self.alu.zero:
                    self.instructions_stack.push(operand)

            case OpCode.JNE:
                if not self.alu.zero:
                    self.instructions_stack.push(operand)

            case OpCode.ADD:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.alu.add(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.SUB:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.alu.sub(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.MUL:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.alu.mul(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.DIV:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                assert b != 0, "Division by zero"

                self.alu.div(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.INC:
                a = self.data_stack.pop()

                self.alu.add(a, 1)
                self.data_stack.push(self.alu.result)

            case OpCode.DEC:
                a = self.data_stack.pop()

                self.alu.sub(a, 1)
                self.data_stack.push(self.alu.result)

            case OpCode.SAVE:
                assert not self.data_stack.is_empty(), "Stack is empty"
                self.data_memory.write(self.base_pointer + operand, self.data_stack.peek())

            case OpCode.HALT:
                return False

        self.increment_instruction_counter()
        return True

    def run(self):
        self.instructions_stack.push(0)

        while True:
            command_pointer = self.instructions_stack.pop()
            command = self.instructions_memory.read(command_pointer)
            result = self.handle_command(command)
            # print(command, self.data_stack)
            self.tick()

            if not result:
                break

            if self.instructions_stack.is_empty():
                self.instructions_stack.push(command_pointer + 1)

    def __str__(self):
        return f"ControlUnit: time={self._time}, instructions executed={self._instruction_counter}"

    def __repr__(self):
        return str(self)
