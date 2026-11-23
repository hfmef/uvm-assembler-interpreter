"""Проверяем байты из методички и выполнение команд."""

import tempfile
import unittest
from pathlib import Path

from src.assembler import assemble, encode, parse_program
from src.vm import VirtualMachine, decode


class UvmTests(unittest.TestCase):
    """Проверки ассемблера и интерпретатора."""

    def test_reference_bytes(self):
        """Сравниваем четыре команды с образцами варианта 7."""
        samples = (
            ("R25 = 169", "ad 54 20 03"),
            ("R0 = M[591]", "84 27 01 00 00 00"),
            ("M[153] = R3", "be 4c 00 00 c0 00"),
            ("M[193] = sgn(R0)", "62 10 0c 00 00 00"),
        )
        for source, expected in samples:
            with self.subTest(source=source):
                instruction = parse_program(source)[0]
                self.assertEqual(encode(instruction), bytes.fromhex(expected))
                decoded, offset = decode(encode(instruction), 0)
                self.assertEqual(decoded, instruction)
                self.assertEqual(offset, len(encode(instruction)))

    def test_copy_array(self):
        """Проверяем копирование массива в другую область памяти."""
        lines = []
        for index, value in enumerate((7, 3, 11)):
            lines.extend((f"R0 = {value}", f"M[{500 + index}] = R0"))
        for index in range(3):
            lines.extend((f"R0 = M[{500 + index}]",
                          f"M[{600 + index}] = R0"))
        vm = VirtualMachine()
        vm.run(assemble(parse_program("\n".join(lines))))
        self.assertEqual(vm.memory[600:603], [7, 3, 11])

    def test_sgn_vector(self):
        """Проверяем sgn над вектором из семи элементов."""
        values = (0, 5, 12, 1, 9, 3, 7)
        lines = []
        for index, value in enumerate(values):
            lines.extend((f"R0 = {value}", f"M[{700 + index}] = R0"))
        for index in range(len(values)):
            lines.extend((f"R0 = M[{700 + index}]",
                          f"M[{700 + index}] = sgn(R0)"))
        vm = VirtualMachine()
        vm.run(assemble(parse_program("\n".join(lines))))
        self.assertEqual(vm.memory[700:707], [0, 1, 1, 1, 1, 1, 1])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dump.csv"
            vm.dump_csv(path, 700, 706)
            self.assertIn("700,0", path.read_text())


if __name__ == "__main__":
    unittest.main()
