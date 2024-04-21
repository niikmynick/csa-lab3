from io_managers.input_manager import InputManager
from io_managers.output_manager import OutputManager


class Memory:
    def __init__(self):
        self._memory = {}
        self._last_allocated = 0

    def allocate(self, size: int) -> int:
        base_pointer = self.get_last_allocated()
        for i in range(size):
            self._memory[base_pointer + i] = None

        self._last_allocated += size

        return base_pointer

    def get_last_allocated(self):
        return self._last_allocated

    def read(self, key):
        assert key in self._memory, f"Key {key} not found in memory"

        cell = self._memory.get(key)

        assert not isinstance(cell, OutputManager), "Cannot read from output manager"

        if isinstance(cell, InputManager):
            cell.read()
            value = cell.get_input()
        else:
            value = cell

        return value

    def write(self, key, value):
        assert key in self._memory, f"Key {key} not found in memory"

        cell = self._memory.get(key)

        assert not isinstance(cell, InputManager), "Cannot write to input manager"

        if isinstance(cell, OutputManager):
            cell.write(str(value))
        else:
            self._memory[key] = value

    def __str__(self):
        return str(self._memory)

    def __repr__(self):
        return str(self._memory)
