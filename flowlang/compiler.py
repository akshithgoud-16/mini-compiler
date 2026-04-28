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

        return {
            "tokens": "\n".join(str(token) for token in tokens),
            "ast": json.dumps(ast_to_dict(ast), indent=2),
            "ir": str(ir),
            "optimized_ir": str(optimized_ir),
            "assembly": assembly,
            "python": python_code,
        }
