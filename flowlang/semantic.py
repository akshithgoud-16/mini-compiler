from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import (
    Assignment,
    BinaryOperation,
    Identifier,
    Number,
    PrintStatement,
    Program,
    WhenStatement,
    VarDeclaration,
    LoopStatement,
    String,
    Boolean,
)


class SemanticError(Exception):
    pass


@dataclass
class SemanticAnalyzer:
    """Check variable use and basic expression validity."""

    symbols: dict[str, int] = field(default_factory=dict)

    def analyze(self, program: Program) -> None:
        for statement in program.statements:
            self.visit(statement)

    def visit(self, node) -> None:
        if isinstance(node, VarDeclaration):
            if node.init is not None:
                self.visit_expression(node.init)
            self.symbols[node.name] = 1
            return
        if isinstance(node, Assignment):
            if node.name not in self.symbols:
                raise SemanticError(f"Variable '{node.name}' assigned before declaration")
            self.visit_expression(node.expression)
            return
        if isinstance(node, WhenStatement):
            self.visit_expression(node.condition)
            for statement in node.body:
                self.visit(statement)
            return
        if isinstance(node, LoopStatement):
            self.visit_expression(node.condition)
            for statement in node.body:
                self.visit(statement)
            return
        if isinstance(node, PrintStatement):
            self.visit_expression(node.expression)
            return
        if node.__class__.__name__ == "AskStatement":
            # Ask assigns input to a variable; ensure the variable is declared
            name = getattr(node, "name", None)
            if name is None or name not in self.symbols:
                raise SemanticError(f"Variable '{name}' used in ask before declaration")
            # prompt may be a string node; that's fine
            return
        raise SemanticError(f"Unsupported AST node: {node.__class__.__name__}")

    def visit_expression(self, node) -> None:
        if isinstance(node, Number):
            return
        if isinstance(node, String):
            return
        if isinstance(node, Boolean):
            return
        if isinstance(node, Identifier):
            if node.name not in self.symbols:
                raise SemanticError(f"Variable '{node.name}' used before declaration")
            return
        if isinstance(node, BinaryOperation):
            self.visit_expression(node.left)
            self.visit_expression(node.right)
            if node.operator not in {"+", "-", "*", "/", ">", "<", ">=", "<=", "==", "!=", "%", "**", "&&", "||"}:
                raise SemanticError(f"Invalid operator '{node.operator}'")
            return
        raise SemanticError(f"Invalid expression node: {node.__class__.__name__}")
