# UVM Assembler and Interpreter — Practice 3, Variant 7

Python implementation of the configuration management assignment.
The source syntax is algebraic, similar to a high-level language.

## Structure

- `src/assembler.py` — parsing and binary encoding.
- `src/vm.py` — binary decoding, shared memory and execution.
- `run.py`, `run.bat` — command-line interface.
- `tests/` — automated unit tests.
- `examples/` — reference bytes, array copy and three vector tasks.

## Supported instructions

| Source statement | A | Meaning |
| --- | --- | --- |
| `R25 = 169` | 45 | Load constant 169 into register 25 |
| `R0 = M[591]` | 4 | Read memory cell 591 into register 0 |
| `M[153] = R3` | 62 | Write register 3 to memory cell 153 |
| `M[193] = sgn(R0)` | 98 | Write sign of register 0 to cell 193 |

`R` means register; `M` means shared memory. Blank lines and
trailing `#` comments are supported.

The bit fields and byte lengths follow variant 7 of the assignment.
Encoding uses little-endian byte order. Registers are numbered 0–31.
The memory contains 4096 integer cells, with program bytes loaded into
the beginning of the same memory array.

## Requirements

Python 3.10+; no external dependencies.

## Assemble and run (Windows)

```bat
run.bat assemble examples/reference.asm reference.bin --test
run.bat assemble examples/copy.asm copy.bin
run.bat run copy.bin copy.csv 600 602
run.bat assemble examples/vector_1.asm vector_1.bin --test
run.bat run vector_1.bin vector_1.csv 700 706
```

On macOS/Linux, replace `run.bat` with `python3 run.py`.

The assembler prints the binary file size. In test mode it also prints
the intermediate A/B/C fields and encoded bytes. The interpreter writes
a CSV memory dump with columns `address,value`. The address range is
inclusive. Binary outputs and CSV dumps are ignored by Git.

## Test all stages

```bat
python -m unittest discover -s tests -v
```

Reference bytes:

- CONST: `AD 54 20 03`
- READ: `84 27 01 00 00 00`
- WRITE: `BE 4C 00 00 C0 00`
- SGN: `62 10 0C 00 00 00`

## Stage 5: three data sets

`vector_1.asm`, `vector_2.asm`, `vector_3.asm` each initialize
seven values at addresses 700–706, apply `sgn()` elementwise,
and overwrite the original vector. Expected results:

- vector 1: `0,1,1,1,1,1,1`
- vector 2: `1,0,0,1,1,1,1`
- vector 3: `1,1,1,1,1,1,1`

## Notes

The `sgn` operation returns -1, 0, or 1 for negative, zero, and
positive register values respectively. The constant instruction in
variant 7 has a 14-bit unsigned immediate field; the provided example
programs therefore initialize nonnegative values.
