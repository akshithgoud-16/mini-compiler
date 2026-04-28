from __future__ import annotations

import json

from .ast_nodes import ast_to_dict
from .codegen import CodeGenerator
from .ir import IRGenerator
from .lexer import Lexer
from .optimizer import Optimizer
from .parser import Parser
from .semantic import SemanticAnalyzer


class FlowLangCompiler:
    def __init__(self):
        self.lexer = Lexer
        self.parser = Parser
        self.semantic = SemanticAnalyzer()
        self.ir_generator = IRGenerator()
        self.optimizer = Optimizer()
        self.codegen = CodeGenerator()

    def compile(self, source: str) -> dict[str, str]:
        tokens = self.lexer(source).tokenize()
        ast = self.parser(tokens).parse()
        self.semantic = SemanticAnalyzer()
        self.semantic.analyze(ast)
        ir = self.ir_generator.generate(ast)
        optimized_ir = self.optimizer.optimize(ir)
        assembly = self.codegen.generate_assembly(optimized_ir)
        python_code = self.codegen.generate_python(ast)
        # Format tokens into a clean two-column table: Type | Value (no line:column)
        token_lines = []
        token_lines.append(f"| {'Type'.ljust(18)} | {'Value'.ljust(50)} |")
        token_lines.append(f"|{'-' * 20}|{'-' * 52}|")
        for t in tokens:
            val = t.value if t.value is not None else ""
            # Truncate long values for table neatness
            display_val = str(val)[:50]
            token_lines.append(f"| {t.type.ljust(18)} | {display_val.ljust(50)} |")

        # Build a simple symbol table representation from the semantic analyzer
        symbols = self.semantic.symbols
        if symbols:
            sym_lines = [f"| {'Name'.ljust(18)} | {'Declared'.ljust(10)} |"]
            sym_lines.append(f"|{'-' * 20}|{'-' * 12}|")
            for name in sorted(symbols.keys()):
                sym_lines.append(f"| {name.ljust(18)} | {'yes'.ljust(10)} |")
            symbols_table = "\n".join(sym_lines)
        else:
            symbols_table = "(no symbols)"

        return {
            "tokens": "\n".join(token_lines),
            "ast": json.dumps(ast_to_dict(ast), indent=2),
            "symbols": symbols_table,
            "ir": str(ir),
            "optimized_ir": str(optimized_ir),
            "assembly": assembly,
            "python": python_code,
        }

        return {
            "tokens": "\n".join(token_lines),
            "ast": json.dumps(ast_to_dict(ast), indent=2),
            "ir": str(ir),
            "optimized_ir": str(optimized_ir),
            "assembly": assembly,
            "python": python_code,
        }
