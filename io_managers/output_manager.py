from sys import stdout


class OutputManager:
    def __init__(self, result_filepath: str, log_filepath: str):
        self.terminal = stdout
        self.output_device = open(result_filepath, 'a')
        self.log_device = open(log_filepath, 'a')

    def write(self, data: str):
        self.terminal.write(data)

        self.output_device.write(data)
        self.output_device.flush()

    def log(self, data):
        self.log_device.write(data)
        self.log_device.flush()
