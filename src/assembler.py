"""Алгебраический ассемблер варианта 7."""

from dataclasses import dataclass
from pathlib import Path

SPECS = {
    "CONST": (45, (7, 14, 5), 4),
    "READ": (4, (7, 31, 5), 6),
    "WRITE": (62, (7, 31, 5), 6),
    "SGN": (98, (7, 5, 31), 6),
}


@dataclass(frozen=True)
class Instruction:
    """Команда в промежуточном представлении."""

    name: str
    a: int
    b: int
    c: int


def parse_register(target: str, value: str) -> Instruction:
    """Разбираем запись в регистр."""
    reg = int(target[1:])
    if value.startswith("M[") and value.endswith("]"):
        return Instruction("READ", 4, int(value[2:-1]), reg)
    return Instruction("CONST", 45, int(value), reg)


def parse_memory(target: str, value: str) -> Instruction:
    """Разбираем запись в память."""
    addr = int(target[2:-1])
    if value.startswith("sgn(R") and value.endswith(")"):
        return Instruction("SGN", 98, int(value[5:-1]), addr)
    if value.startswith("R") and value[1:].isdigit():
        return Instruction("WRITE", 62, addr, int(value[1:]))
    raise ValueError(f"Unknown memory operand: {value}")


def parse_line(line: str) -> Instruction | None:
    """Разбираем присваивание с регистром и памятью."""
    line = line.split("#", 1)[0].strip().replace(" ", "")
    if not line:
        return None
    if "=" not in line:
        raise ValueError(f"Expected assignment: {line}")
    target, value = line.split("=", 1)
    if target.startswith("R") and target[1:].isdigit():
        return parse_register(target, value)
    if target.startswith("M[") and target.endswith("]"):
        return parse_memory(target, value)
    raise ValueError(f"Unknown instruction: {line}")


def parse_program(source: str) -> list[Instruction]:
    """Создаём список команд из исходного текста."""
    return [item for line in source.splitlines()
            if (item := parse_line(line)) is not None]


def encode(instruction: Instruction) -> bytes:
    """Преобразуем поля A, B, C в машинные байты."""
    opcode, widths, size = SPECS[instruction.name]
    if instruction.a != opcode:
        raise ValueError("Incorrect opcode")
    number = 0
    shift = 0
    for value, width in zip(
        (instruction.a, instruction.b, instruction.c), widths
    ):
        if not 0 <= value < (1 << width):
            raise ValueError(f"Field {value} exceeds {width} bits")
        number |= value << shift
        shift += width
    return number.to_bytes(size, "little")


def assemble(program: list[Instruction]) -> bytes:
    """Объединяем команды в двоичную программу."""
    return b"".join(encode(item) for item in program)


def assemble_file(source: Path, output: Path) -> list[Instruction]:
    """Собираем исходный файл в бинарный."""
    program = parse_program(source.read_text(encoding="utf-8"))
    output.write_bytes(assemble(program))
    return program
