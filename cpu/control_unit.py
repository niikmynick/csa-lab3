from memory.stack import Stack
from cpu.alu import ALU
from cpu.interruption import Interruption, InterruptionType
from memory.memory import Memory
from asm.instruction import Instruction, OpCode, OpType
from io_managers.logger import Logger, LogLevel, Place


class ControlUnit:
    def __init__(self):
        self._time: int = 0
        self._instruction_counter: int = 0
        self._exit_flag = False
        self._command_pointer = 0
        self._interruption_flag = False

        self._data_stack = Stack()
        self._instructions_stack = Stack()
        self._interruptions_stack = Stack()
        self.alu = ALU()

        self.instructions_memory = None
        self.data_memory = None

        self.logger = None

        self.input_address = None
        self.output_address = None
        self.base_pointer = None

    def set_logger(self, logger: Logger):
        self.logger = logger

    def set_input_address(self, input_address: int):
        self.input_address = input_address

    def set_output_address(self, output_address: int):
        self.output_address = output_address

    def set_base_pointer(self, base_pointer: int):
        self.base_pointer = base_pointer

    def connect_instructions_memory(self, instructions_memory: Memory):
        self.instructions_memory = instructions_memory

    def connect_data_memory(self, data_memory: Memory):
        self.data_memory = data_memory

    def set_exit_flag(self, exit_flag: bool):
        self._exit_flag = exit_flag

    def set_command_pointer(self, command_pointer: int):
        self._command_pointer = command_pointer

    def set_interruption_flag(self, interruption_flag: bool):
        self._interruption_flag = interruption_flag

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

            self.tick()

            self.logger.log(LogLevel.DEBUG, Place.INTER, f"Processing {interruption}")

            match interruption.interruption_type:
                case InterruptionType.INPUT:
                    if interruption.message is not None:
                        self.data_memory.write(self.output_address, interruption.message)
                        self.tick()

                    self.logger.log(LogLevel.INFO, Place.INPUT, "Reading input")
                    value = self.data_memory.read(self.input_address)
                    self.tick()

                    self.logger.log(LogLevel.INFO, Place.INPUT, f"Read value: {value}")

                    self.tick()

                    if value.isnumeric():
                        self._data_stack.push(int(value))
                        self.tick()

                    else:
                        self._data_stack.push(value)

                    self.tick()

                case InterruptionType.OUTPUT:
                    if interruption.message is not None:
                        self.data_memory.write(self.output_address, interruption.message)
                        self.tick()
                        continue
                    self.tick()

                    self.logger.log(LogLevel.INFO, Place.OUTPUT, "Writing output")

                    value = self._data_stack.pop()
                    self.data_memory.write(self.output_address, value)
                    self.tick()

                case InterruptionType.HALT:
                    self._exit_flag = True
                    self.tick()
                    self.logger.log(LogLevel.INFO, Place.SYSTEM, "Halting")
                    break

                case InterruptionType.ERROR:
                    self.logger.log(LogLevel.ERROR, Place.SYSTEM, f"Error: {interruption.message}")

                    interruption_halt = Interruption(InterruptionType.HALT)
                    self._interruptions_stack.push(interruption_halt)
                    self.tick()

                    interruption_output = Interruption(InterruptionType.OUTPUT,
                                                       f"An error occurred: {interruption.message}")
                    self._interruptions_stack.push(interruption_output)
                    self.tick()

            self.logger.log(LogLevel.DEBUG, Place.INTER, f"Finished processing {interruption}")

        self._interruption_flag = False

    def handle_command(self):
        instruction = self._instructions_stack.pop()

        opcode = instruction.opcode
        operand = instruction.operand
        optype = instruction.operand_type

        self.logger.log(LogLevel.INFO, Place.INSTR, f"Processing {opcode.name} "
                                                    f"{optype.name if optype != OpType.NOPE else ''} "
                                                    f"{operand if operand is not None else ''}")

        match opcode:
            case OpCode.PUSH:
                if optype == OpType.VALUE:
                    self._data_stack.push(operand)
                    self.tick()

                elif optype == OpType.ADDRESS:
                    value = self.data_memory.read(self.base_pointer + operand)
                    self.tick()

                    if value is None:
                        interruption = Interruption(InterruptionType.ERROR, "No value at address")
                        self._interruptions_stack.push(interruption)
                        self.tick()
                        return

                    self._data_stack.push(value)
                    self.tick()

            case OpCode.POP:
                if self._data_stack.is_empty():
                    interruption = Interruption(InterruptionType.ERROR, "Stack is empty")
                    self._interruptions_stack.push(interruption)
                    self.tick()
                else:
                    self._data_stack.pop()
                    self.tick()

                self.tick()

            case OpCode.READ:
                interruption = Interruption(InterruptionType.INPUT)
                self._interruptions_stack.push(interruption)
                self.tick()

            case OpCode.WRITE:
                message = self._data_stack.pop()
                interruption = Interruption(InterruptionType.OUTPUT, message)
                self._interruptions_stack.push(interruption)
                self.tick()

            case OpCode.COMPARE:
                #     a > b -> 1
                #     a < b -> -1
                #     a == b -> 0
                b = self._data_stack.pop()
                self.tick()
                a = self._data_stack.pop()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Comparing {a} and {b}")

                self.alu.compare(a, b)
                self.tick()

            case OpCode.JUMP:
                command = self.instructions_memory.read(operand)
                self.tick()

                self._instructions_stack.push(command)
                self.tick()

                self._command_pointer = operand + 1

            case OpCode.JLA:
                if not self.alu.zero and not self.alu.negative:
                    self._instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))
                    self.tick()
                self.tick()

            case OpCode.JLE:
                if self.alu.negative:
                    self._instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))
                    self.tick()
                self.tick()

            case OpCode.JEQ:
                if self.alu.zero:
                    self._instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))
                    self.tick()
                self.tick()

            case OpCode.JNE:
                if not self.alu.zero:
                    self._instructions_stack.push(Instruction(OpCode.JUMP, operand, OpType.ADDRESS))
                    self.tick()
                self.tick()

            case OpCode.ADD:
                b = self._data_stack.pop()
                self.tick()
                a = self._data_stack.pop()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Adding {a} and {b}")

                self.alu.add(a, b)
                self.tick()
                self._data_stack.push(self.alu.result)
                self.tick()

            case OpCode.SUB:
                b = self._data_stack.pop()
                self.tick()
                a = self._data_stack.pop()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Subtracting {a} and {b}")

                self.alu.sub(a, b)
                self.tick()
                self._data_stack.push(self.alu.result)
                self.tick()

            case OpCode.MUL:
                b = self._data_stack.pop()
                self.tick()
                a = self._data_stack.pop()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Multiplying {a} and {b}")

                self.alu.mul(a, b)
                self.tick()
                self._data_stack.push(self.alu.result)
                self.tick()

            case OpCode.DIV:
                b = self._data_stack.pop()
                self.tick()
                a = self._data_stack.pop()
                self.tick()

                if b == 0:
                    interruption = Interruption(InterruptionType.ERROR, "Division by zero")
                    self._interruptions_stack.push(interruption)
                    self.tick()
                else:
                    self.logger.log(LogLevel.DEBUG, Place.ALU, f"Dividing {a} and {b}")

                    self.alu.div(a, b)
                    self.tick()
                    self._data_stack.push(self.alu.result)
                    self.tick()
                self.tick()

            case OpCode.INC:
                a = self._data_stack.pop()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Incrementing {a}")

                self.alu.add(a, 1)
                self.tick()
                self._data_stack.push(self.alu.result)
                self.tick()

            case OpCode.DEC:
                a = self._data_stack.pop()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Decrementing {a}")

                self.alu.sub(a, 1)
                self.tick()
                self._data_stack.push(self.alu.result)
                self.tick()

            case OpCode.SAVE:
                if self._data_stack.is_empty():
                    interruption = Interruption(InterruptionType.ERROR, "Stack is empty")
                    self._interruptions_stack.push(interruption)
                    self.tick()
                self.tick()

                self.data_memory.write(self.base_pointer + operand, self._data_stack.peek())
                self.tick()

            case OpCode.HALT:
                interruption = Interruption(InterruptionType.HALT)
                self._interruptions_stack.push(interruption)
                self.tick()

            case _:
                interruption = Interruption(InterruptionType.ERROR, f"Unknown opcode: {opcode}")
                self._interruptions_stack.push(interruption)
                self.tick()

        self.increment_instruction_counter()

    def run(self):
        self.logger.log(LogLevel.INFO, Place.SYSTEM, "Starting execution")

        assert self.instructions_memory is not None, "Instructions memory is not connected"
        assert self.data_memory is not None, "Data memory is not connected"
        assert self.input_address is not None, "Input address is not set"
        assert self.output_address is not None, "Output address is not set"
        assert self.base_pointer is not None, "Base pointer is not set"

        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Initial state: {self}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Instructions memory: {self.instructions_memory}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Data memory: {self.data_memory}")

        while True:
            self.handle_interruption()

            if self._exit_flag:
                self.logger.log(LogLevel.INFO, Place.SYSTEM, f"Execution finished, state: {self}")
                break

            if self._instructions_stack.is_empty():
                command = self.instructions_memory.read(self._command_pointer)
                self.tick()

                self._instructions_stack.push(command)
                self.tick()

                self._command_pointer += 1

            self.tick()

            self.logger.log(LogLevel.DEBUG, Place.SYSTEM, str(self))

            self.handle_command()

    def __str__(self):
        return f"ControlUnit: time={self._time}, instructions executed={self._instruction_counter}"

    def __repr__(self):
        return str(self)
