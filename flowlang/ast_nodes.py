from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    statements: list[ASTNode] = field(default_factory=list)


@dataclass
class Assignment(ASTNode):
    name: str
    expression: ASTNode


@dataclass
class WhenStatement(ASTNode):
    condition: ASTNode
    body: list[ASTNode]


@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode


@dataclass
class BinaryOperation(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class Number(ASTNode):
    value: int


@dataclass
class Identifier(ASTNode):
    name: str


def ast_to_dict(node: ASTNode) -> Any:
    if isinstance(node, Program):
        return {"type": "Program", "statements": [ast_to_dict(stmt) for stmt in node.statements]}
    if isinstance(node, Assignment):
        return {"type": "Assignment", "name": node.name, "expression": ast_to_dict(node.expression)}
    if isinstance(node, WhenStatement):
        return {
            "type": "WhenStatement",
            "condition": ast_to_dict(node.condition),
            "body": [ast_to_dict(stmt) for stmt in node.body],
        }
    if isinstance(node, PrintStatement):
        return {"type": "PrintStatement", "expression": ast_to_dict(node.expression)}
    if isinstance(node, BinaryOperation):
        return {
            "type": "BinaryOperation",
            "operator": node.operator,
            "left": ast_to_dict(node.left),
            "right": ast_to_dict(node.right),
        }
    if isinstance(node, Number):
        return {"type": "Number", "value": node.value}
    if isinstance(node, Identifier):
        return {"type": "Identifier", "name": node.name}
    return {"type": node.__class__.__name__}
