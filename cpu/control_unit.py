from memory.stack import Stack
from cpu.alu import ALU
from cpu.interruption import Interruption, InterruptionType
from memory.memory import Memory
from asm.instruction import Instruction, OpCode, OpType
from io_managers.logger import Logger, LogLevel, Place


class ControlUnit:
    def __init__(self, instruction_memory: Memory, data_memory: Memory,
                 input_address: int, output_address: int,
                 base_pointer: int = 0,
                 logger: Logger = None
                 ):

        self._time: int = 0
        self._instruction_counter: int = 0
        self._exit_flag = False
        self._command_pointer = 0
        self._interruption_flag = False

        self.data_stack = Stack()
        self.instructions_stack = Stack()
        self._interruptions_stack = Stack()
        self.alu = ALU()

        self.instructions_memory = instruction_memory
        self.data_memory = data_memory

        self.logger = logger

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

    def handle_interruption(self):
        self.logger.log(LogLevel.DEBUG, Place.INTER, f"Have {self._interruptions_stack.size()} interruptions")

        while not self._interruptions_stack.is_empty():
            interruption: Interruption = self._interruptions_stack.pop()
            self._interruption_flag = True

            self.logger.log(LogLevel.DEBUG, Place.INTER, f"Processing {interruption}")

            match interruption.interruption_type:
                case InterruptionType.INPUT:
                    if interruption.message is not None:
                        self.data_memory.write(self.output_address, interruption.message)

                    self.logger.log(LogLevel.INFO, Place.INTER, "Reading input")
                    value = self.data_memory.read(self.input_address)

                    self.logger.log(LogLevel.INFO, Place.INTER, f"Read value: {value}")

                    self.data_stack.push(None)
                    if value.isnumeric():
                        self.data_stack.push(int(value))
                        return

                    for symbol in value[::-1]:
                        self.data_stack.push(symbol)

                case InterruptionType.OUTPUT:
                    if interruption.message is not None:
                        self.data_memory.write(self.output_address, interruption.message)
                        continue

                    if self.data_stack.is_empty():
                        interruption_error = Interruption(InterruptionType.ERROR, "Stack is empty")
                        self._interruptions_stack.push(interruption_error)
                        continue

                    self.logger.log(LogLevel.INFO, Place.INTER, "Writing output")

                    while True:
                        symbol = self.data_stack.pop()
                        if symbol is None:
                            break

                        self.data_memory.write(self.output_address, symbol)

                case InterruptionType.HALT:
                    self._exit_flag = True
                    self.logger.log(LogLevel.INFO, Place.INTER, "Halting")
                    break

                case InterruptionType.ERROR:
                    self.logger.log(LogLevel.ERROR, Place.INTER, f"Error: {interruption.message}")

                    interruption_halt = Interruption(InterruptionType.HALT)
                    self._interruptions_stack.push(interruption_halt)

                    interruption_output = Interruption(InterruptionType.OUTPUT, interruption.message)
                    self._interruptions_stack.push(interruption_output)

        self._interruption_flag = False

    def handle_command(self):
        instruction = self.instructions_stack.pop()

        opcode = instruction.opcode
        operand = instruction.operand
        optype = instruction.operand_type

        self.logger.log(LogLevel.INFO, Place.INSTR, f"Processing {opcode.name} {optype.name if optype != OpType.NOPE else ''} {operand if operand is not None else ''}")

        match opcode:
            case OpCode.PUSH:
                if optype == OpType.VALUE:
                    self.data_stack.push(operand)

                elif optype == OpType.ADDRESS:
                    value = self.data_memory.read(self.base_pointer + operand)
                    self.data_stack.push(value)

            case OpCode.POP:
                self.data_stack.pop()

            case OpCode.READ:
                interruption = Interruption(InterruptionType.INPUT, '> ')
                self._interruptions_stack.push(interruption)

            case OpCode.WRITE:
                interruption = Interruption(InterruptionType.OUTPUT)
                self._interruptions_stack.push(interruption)

            case OpCode.COMPARE:
                #     a > b -> 1
                #     a < b -> -1
                #     a == b -> 0
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Comparing {a} and {b}")

                self.alu.compare(a, b)

            case OpCode.JUMP:
                command = self.instructions_memory.read(operand)
                self.instructions_stack.push(command)
                self._command_pointer = operand + 1

            case OpCode.JLA:
                if not self.alu.zero and not self.alu.negative:
                    self.instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))

            case OpCode.JLE:
                if self.alu.negative:
                    self.instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))

            case OpCode.JEQ:
                if self.alu.zero:
                    self.instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))

            case OpCode.JNE:
                if not self.alu.zero:
                    self.instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))

            case OpCode.ADD:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Adding {a} and {b}")

                self.alu.add(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.SUB:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Subtracting {a} and {b}")

                self.alu.sub(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.MUL:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Multiplying {a} and {b}")

                self.alu.mul(a, b)
                self.data_stack.push(self.alu.result)

            case OpCode.DIV:
                b = self.data_stack.pop()
                a = self.data_stack.pop()

                if b == 0:
                    interruption = Interruption(InterruptionType.ERROR, "Division by zero")
                    self._interruptions_stack.push(interruption)
                else:
                    self.logger.log(LogLevel.DEBUG, Place.ALU, f"Dividing {a} and {b}")

                    self.alu.div(a, b)
                    self.data_stack.push(self.alu.result)

            case OpCode.INC:
                a = self.data_stack.pop()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Incrementing {a}")

                self.alu.add(a, 1)
                self.data_stack.push(self.alu.result)

            case OpCode.DEC:
                a = self.data_stack.pop()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Decrementing {a}")

                self.alu.sub(a, 1)
                self.data_stack.push(self.alu.result)

            case OpCode.SAVE:
                if self.data_stack.is_empty():
                    interruption = Interruption(InterruptionType.ERROR, "Stack is empty")
                    self._interruptions_stack.push(interruption)

                self.data_memory.write(self.base_pointer + operand, self.data_stack.peek())

            case OpCode.HALT:
                interruption = Interruption(InterruptionType.HALT)
                self._interruptions_stack.push(interruption)

            case _:
                interruption = Interruption(InterruptionType.ERROR, f"Unknown opcode: {opcode}")
                self._interruptions_stack.push(interruption)

        self.increment_instruction_counter()

    def run(self):
        self.logger.log(LogLevel.INFO, Place.SYSTEM, "Starting execution")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Initial state: {self}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Instructions memory: {self.instructions_memory}")

        while True:
            self.handle_interruption()

            if self._exit_flag:
                break

            if self.instructions_stack.is_empty():
                command = self.instructions_memory.read(self._command_pointer)
                self.instructions_stack.push(command)
                self._command_pointer += 1

            self.logger.log(LogLevel.DEBUG, Place.SYSTEM, str(self))

            self.handle_command()

            self.tick()

    def __str__(self):
        return f"ControlUnit: time={self._time}, instructions executed={self._instruction_counter}"

    def __repr__(self):
        return str(self)
