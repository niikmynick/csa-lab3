import os
import tempfile

import pytest

from asm.assembler import Assembler
from machine import Machine


@pytest.mark.golden_test("./golden/test/*.yml")
def test_translator_asm_and_machine(golden):
    assembler = Assembler()
    machine = Machine()

    with tempfile.TemporaryDirectory() as directory:
        source = os.path.join(directory, "source.asm")
        input_stream = os.path.join(directory, "input.txt")
        target = os.path.join(directory, "target.o")
        out_file = os.path.join(directory, "out.txt")
        log_file = os.path.join(directory, "log.txt")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        assembler.assemble(source, target)
        machine.configure(target, input_stream, out_file, log_file)
        machine.run()

        with open(target, 'rb') as file:
            temp = file.read().strip()
            code = ''
            for byte in temp:
                code += f'{byte:08b}'

        with open(out_file, encoding="utf-8") as file:
            out = file.read().strip()

        with open(log_file, encoding="utf-8") as file:
            log = file.read().strip()

        assert code == golden.out["out_bin"]
        assert out == golden.out["out_stdout"]
        assert log == golden.out["out_log"]
