from __future__ import annotations

import argparse
import sys
import io
import contextlib
import traceback

from flowlang.compiler import FlowLangCompiler
from flowlang.lexer import LexerError
from flowlang.parser import ParserError
from flowlang.semantic import SemanticError


DEFAULT_PROGRAM = """x -> 10
y -> 20
folded -> 10 + 20
z -> x + y
when z > 15:
say z
"""


def read_source(file_path: str | None) -> str:
    if file_path:
        with open(file_path, "r", encoding="utf-8") as handle:
            return handle.read()

    # If no file_path provided, and stdin is piped, read from stdin
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data.strip():
            return data

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="FlowLang mini compiler")
    parser.add_argument("--file", help="Path to a FlowLang source file")
    parser.add_argument("--source", help="FlowLang program as an inline string")
    parser.add_argument("--interactive", action="store_true", help="Enter FlowLang program manually (terminate with a line containing only END)")
    args = parser.parse_args()

    if args.interactive:
        print("Enter FlowLang program. End with a single line containing only: END")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
        except EOFError:
            # User sent EOF; accept what we have
            pass
        source = "\n".join(lines) + "\n"
    else:
        source = args.source if args.source else read_source(args.file)

    # If still no source (no file, no --source, and no piped stdin), prompt interactively by default
    if source is None:
        print("No source provided. Enter FlowLang program. End with a single line containing only: END")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
        except EOFError:
            pass
        source = "\n".join(lines) + "\n"

    compiler = FlowLangCompiler()

    try:
        result = compiler.compile(source)
    except (LexerError, ParserError, SemanticError, ZeroDivisionError) as exc:
        print(f"Compilation failed: {exc}")
        return 1

    print("=== PHASE 1: LEXICAL ANALYSIS ===")
    print("Tokens (type, value, line:column):")
    print(result["tokens"])
    print()

    print("=== PHASE 2: SYNTAX ANALYSIS (AST) ===")
    print("Abstract Syntax Tree (JSON):")
    print(result["ast"])
    print()

    print("=== PHASE 3: INTERMEDIATE REPRESENTATION (3-address code) ===")
    print("Generated IR:")
    print(result["ir"])
    print()

    print("=== PHASE 4: OPTIMIZATION ===")
    print("Optimized IR (constant folding applied):")
    print(result["optimized_ir"])
    print()

    print("=== PHASE 5: TARGET CODE GENERATION ===")
    print("Pseudo-assembly:")
    print(result["assembly"])
    print()

    print("Equivalent Python code:")
    print(result["python"])
    print()
    print("=== PHASE 6: RUN GENERATED PYTHON ===")
    python_code = result["python"]
    try:
        buf = io.StringIO()
        exec_globals: dict = {}
        with contextlib.redirect_stdout(buf):
            exec(python_code, exec_globals)
        program_output = buf.getvalue()
        print("Program output:")
        print(program_output if program_output else "(no output)")
    except Exception:
        print("Runtime error while executing generated Python:")
        traceback.print_exc()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
