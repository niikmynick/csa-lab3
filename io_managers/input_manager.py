from sys import stdin


class InputManager:
    def __init__(self):
        self._input = None
        self.input_device = stdin

    def get_input(self):
        return self._input

    def set_input(self, text):
        self._input = text

    def read(self):
        self.set_input(self.input_device.readline().strip())
