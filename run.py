"""Командный интерфейс ассемблера и интерпретатора."""

import argparse
from pathlib import Path

from src.assembler import assemble_file
from src.vm import VirtualMachine


def main() -> None:
    """Обрабатываем параметры запуска."""
    parser = argparse.ArgumentParser(description="Variant 7 UVM")
    sub = parser.add_subparsers(dest="mode", required=True)
    assembler = sub.add_parser("assemble")
    assembler.add_argument("source", type=Path)
    assembler.add_argument("output", type=Path)
    assembler.add_argument("--test", action="store_true")
    interpreter = sub.add_parser("run")
    interpreter.add_argument("binary", type=Path)
    interpreter.add_argument("dump", type=Path)
    interpreter.add_argument("start", type=int)
    interpreter.add_argument("end", type=int)
    args = parser.parse_args()
    if args.mode == "assemble":
        program = assemble_file(args.source, args.output)
        print(f"Binary size: {args.output.stat().st_size} bytes")
        if args.test:
            for instruction in program:
                print(f"A={instruction.a}, B={instruction.b}, "
                      f"C={instruction.c}")
            print("Bytes:", args.output.read_bytes().hex(" "))
    else:
        vm = VirtualMachine()
        count = vm.run(args.binary.read_bytes())
        vm.dump_csv(args.dump, args.start, args.end)
        print(f"Executed: {count}; dump: {args.dump}")


if __name__ == "__main__":
    main()
