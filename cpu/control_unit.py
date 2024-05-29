from memory.stack import Stack
from cpu.alu import ALU
from cpu.interruption import Interruption, InterruptionType
from memory.memory import Memory
from asm.instruction import Instruction, OpCode, OpType
from io_managers.logger import Logger, LogLevel, Place
from exceptions import EmptyStackException


class ControlUnit:
    def __init__(self):
        self._time: int = 0
        self._instruction_counter: int = 0
        self._exit_flag = False
        self._command_pointer = 0
        self._interruption_flag = False

        self._data_stack = Stack()
        self._return_stack = Stack()
        self.alu = ALU()

        self.instructions_memory = None
        self.data_memory = None

        self.logger = None

        self.interruption = None
        self.interruption_vec = None
        self.interruption_times = []

    def set_logger(self, logger: Logger):
        self.logger = logger

    def set_schedule(self, schedule: list[int]):
        self.interruption_times = schedule

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
        self.tick()

    def increment_command_pointer(self):
        self._command_pointer += 1
        self.tick()

    def get_instruction_counter(self) -> int:
        return self._instruction_counter

    def handle_interruption(self):
        if self.interruption is None:
            return

        self._interruption_flag = True
        self.tick()

        self.logger.log(LogLevel.DEBUG, Place.INTER, f"Processing {self.interruption}")

        match self.interruption.interruption_type:
            case InterruptionType.INPUT:
                if self.interruption_vec is None:
                    self.interruption = None
                    self._interruption_flag = False
                    self.tick()
                    return

                self._return_stack.push(self._command_pointer)
                self.tick()

                self._command_pointer = self.interruption_vec
                self.tick()

                flow_changed = self.handle_command()
                while not flow_changed:
                    self.increment_command_pointer()
                    self.increment_instruction_counter()
                    flow_changed = self.handle_command()

                    if self.interruption_times and self._time > self.interruption_times[0]:
                        self.interruption_times.pop(0)
                        self.data_memory.read(0)

            case InterruptionType.ERROR:
                self.logger.log(LogLevel.ERROR, Place.SYSTEM, f"Error: {self.interruption.message}")

                self._exit_flag = True
                self.tick()

                self.logger.log(LogLevel.INFO, Place.SYSTEM, "Halting")

            case InterruptionType.HALT:
                self._exit_flag = True
                self.tick()

                self.logger.log(LogLevel.INFO, Place.SYSTEM, "Halting")

        self.interruption = None
        self._interruption_flag = False
        self.tick()

    def handle_command(self):
        instruction: Instruction = self.instructions_memory.read(self._command_pointer)
        self.tick()

        opcode = instruction.opcode
        operand = instruction.operand
        optype = instruction.operand_type

        flow_changed = False

        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Data stack: {self._data_stack}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, str(self))
        self.logger.log(LogLevel.INFO, Place.INSTR, f"Processing {opcode.name}" +
                        (f" {optype.name} {operand}" if optype != OpType.NOPE else ""))

        match opcode:
            case OpCode.PUSH:
                self._data_stack.push(operand)
                self.tick()

            case OpCode.DUPLICATE:
                value = self._data_stack.peek()
                self.tick()

                self._data_stack.push(value)
                self.tick()

            case OpCode.POP:
                if self._data_stack.is_empty():
                    self.interruption = Interruption(InterruptionType.ERROR, "Stack is empty")
                    self.tick()

                else:
                    self._data_stack.pop()
                    self.tick()

                self.tick()

            case OpCode.READ:
                if optype == OpType.NOPE:
                    address = self._data_stack.pop()
                    self.tick()
                    value = self.data_memory.read(address)
                    self.tick()
                else:
                    value = self.data_memory.read(operand)
                    self.tick()

                self._data_stack.push(value)
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
                self._data_stack.push(self.alu.result)
                self.tick()

            case OpCode.JUMP:
                self._command_pointer = operand
                self.tick()
                flow_changed = True

            case OpCode.JLA:
                value = self._data_stack.pop()
                self.tick()
                if value == 1:
                    self._command_pointer = operand
                    self.tick()
                    flow_changed = True

                self.tick()

            case OpCode.JLE:
                value = self._data_stack.pop()
                self.tick()
                if value == -1:
                    self._command_pointer = operand
                    self.tick()
                    flow_changed = True

                self.tick()

            case OpCode.JEQ:
                value = self._data_stack.pop()
                self.tick()
                if value == 0:
                    self._command_pointer = operand
                    self.tick()
                    flow_changed = True

                self.tick()

            case OpCode.JNE:
                value = self._data_stack.pop()
                self.tick()
                if value != 0:
                    self._command_pointer = operand
                    self.tick()
                    flow_changed = True

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
                    self.interruption = Interruption(InterruptionType.ERROR, "Division by zero")
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

            case OpCode.SWAP:
                b = self._data_stack.pop()
                self.tick()
                a = self._data_stack.pop()
                self.tick()

                self._data_stack.push(b)
                self.tick()

                self._data_stack.push(a)
                self.tick()

            case OpCode.SAVE:
                try:
                    if optype == OpType.NOPE:
                        where = self._data_stack.pop()
                        self.tick()
                    else:
                        where = operand

                    what = self._data_stack.pop()
                    self.tick()

                    self.data_memory.write(where, what)
                    self.tick()

                except EmptyStackException:
                    self.interruption = Interruption(InterruptionType.ERROR, "Stack is empty")
                    self.tick()

                self.tick()

            case OpCode.RETURN:
                self._command_pointer = self._return_stack.pop()
                self.tick()
                flow_changed = True

            case OpCode.HALT:
                self.interruption = Interruption(InterruptionType.HALT)
                self.tick()

            case OpCode.NOP:
                self.tick()

            case _:
                self.interruption = Interruption(InterruptionType.ERROR, f"Unknown opcode: {opcode}")
                self.tick()

        return flow_changed

    def run(self):
        self.logger.log(LogLevel.INFO, Place.SYSTEM, "Starting execution")

        assert self.instructions_memory is not None, "Instructions memory is not connected"
        assert self.data_memory is not None, "Data memory is not connected"

        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Initial state: {self}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Instructions memory: {self.instructions_memory}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Data memory: {self.data_memory}")

        while True:
            if self.interruption_times and self._time >= self.interruption_times[0]:
                self.interruption_times.pop(0)
                self.tick()

                self.interruption = Interruption(InterruptionType.INPUT)
                self.tick()

            self.handle_interruption()

            if self._exit_flag:
                self.logger.log(LogLevel.INFO, Place.SYSTEM, f"Execution finished, state: {self}")
                break

            flow_changed = self.handle_command()
            self.increment_instruction_counter()

            if not flow_changed:
                self.increment_command_pointer()

    def __str__(self):
        return (f"ControlUnit: time={self._time}, "
                f"instructions executed={self._instruction_counter}, "
                f"interruption = {self._interruption_flag}")

    def __repr__(self):
        return str(self)
