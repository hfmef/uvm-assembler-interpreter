"""Интерпретатор УВМ с общей памятью кода и данных."""

import csv
from pathlib import Path

from src.assembler import Instruction, SPECS

MEMORY_SIZE = 4096
OPCODES = {spec[0]: (name, spec) for name, spec in SPECS.items()}


def decode(binary: bytes, offset: int) -> tuple[Instruction, int]:
    """Декодируем одну команду по битовым полям."""
    opcode = binary[offset] & 127
    if opcode not in OPCODES:
        raise ValueError(f"Unknown opcode {opcode} at {offset}")
    name, (_, widths, size) = OPCODES[opcode]
    if offset + size > len(binary):
        raise ValueError("Truncated instruction")
    number = int.from_bytes(binary[offset:offset + size], "little")
    fields = []
    for width in widths:
        fields.append(number & ((1 << width) - 1))
        number >>= width
    return Instruction(name, *fields), offset + size


class VirtualMachine:
    """Модель памяти и регистров учебной машины."""

    def __init__(self, size: int = MEMORY_SIZE):
        """Создаём общую память и 32 регистра."""
        self.memory = [0] * size
        self.registers = [0] * 32

    def execute(self, instruction: Instruction) -> None:
        """Выполняем загрузку, чтение, запись или sgn."""
        name = instruction.name
        b, c = instruction.b, instruction.c
        if name == "CONST":
            self.registers[c] = b
        elif name == "READ":
            self.registers[c] = self.memory[b]
        elif name == "WRITE":
            self.memory[b] = self.registers[c]
        elif name == "SGN":
            value = self.registers[b]
            self.memory[c] = (value > 0) - (value < 0)
        else:
            raise ValueError(f"Unsupported instruction: {name}")

    def run(self, binary: bytes) -> int:
        """Загружаем код в память и выполняем все команды."""
        if len(binary) > len(self.memory):
            raise ValueError("Program exceeds memory")
        for index, byte in enumerate(binary):
            self.memory[index] = byte
        offset = 0
        count = 0
        while offset < len(binary):
            instruction, offset = decode(binary, offset)
            self.execute(instruction)
            count += 1
        return count

    def dump_csv(self, path: Path, start: int, end: int) -> None:
        """Сохраняем диапазон памяти в CSV."""
        if not 0 <= start <= end < len(self.memory):
            raise ValueError("Invalid memory range")
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("address", "value"))
            for address in range(start, end + 1):
                writer.writerow((address, self.memory[address]))
