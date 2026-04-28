from __future__ import annotations

import argparse
import sys
import io
import contextlib
import traceback
import textwrap

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
    def print_box(title: str, content: str, width: int = 88) -> None:
        lines = []
        lines.append("+" + "-" * (width - 2) + "+")
        title_line = f" {title} "
        lines.append("|" + title_line.center(width - 2) + "|")
        lines.append("+" + "=" * (width - 2) + "+")
        if content is None or str(content).strip() == "":
            content_lines = ["(no content)"]
        else:
            raw_lines = str(content).splitlines()
            # If content already looks like a table (lines starting with '|'), keep columns intact
            content_lines = []
            if any(rl.strip().startswith("|") for rl in raw_lines):
                for rl in raw_lines:
                    # remove leading/trailing pipe for clean placement but keep internal pipes
                    inner = rl.strip()
                    if inner.startswith("|") and inner.endswith("|"):
                        inner = inner[1:-1]
                    content_lines.append(inner.strip())
            else:
                for rl in raw_lines:
                    wrapped = textwrap.wrap(rl, width=width - 4) or [""]
                    for w in wrapped:
                        content_lines.append(w)
        for cl in content_lines:
            lines.append("| " + cl.ljust(width - 4) + " |")
        lines.append("+" + "-" * (width - 2) + "+")
        print("\n".join(lines))

    print_box("PHASE 1: LEXICAL ANALYSIS - Tokens (type, value)", result["tokens"])

    print_box("PHASE 2: SYNTAX ANALYSIS (AST)", result["ast"])

    print_box("SYMBOL TABLE", result.get("symbols", "(no symbols)"))

    print_box("PHASE 3: INTERMEDIATE REPRESENTATION (3-address code)", result["ir"])

    print_box("PHASE 4: OPTIMIZATION - Optimized IR (constant folding applied)", result["optimized_ir"])

    print_box("PHASE 5: TARGET CODE GENERATION - Pseudo-assembly", result["assembly"])

    print_box("PHASE 5: TARGET CODE GENERATION - Equivalent Python code", result["python"])

    print_box("PHASE 6: RUN GENERATED PYTHON", "")
    python_code = result["python"]
    try:
        buf = io.StringIO()
        exec_globals: dict = {}
        with contextlib.redirect_stdout(buf):
            exec(python_code, exec_globals)
        program_output = buf.getvalue()
        print_box("Program output", program_output if program_output else "(no output)")
    except Exception:
        print("Runtime error while executing generated Python:")
        traceback.print_exc()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
