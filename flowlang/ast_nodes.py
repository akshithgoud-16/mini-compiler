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
class VarDeclaration(ASTNode):
    name: str
    init: ASTNode | None = None


@dataclass
class LoopStatement(ASTNode):
    condition: ASTNode
    body: list[ASTNode]


@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode


@dataclass
class AskStatement(ASTNode):
    name: str
    prompt: String | None = None


@dataclass
class BinaryOperation(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class Number(ASTNode):
    value: int


@dataclass
class String(ASTNode):
    value: str


@dataclass
class Boolean(ASTNode):
    value: bool


@dataclass
class Identifier(ASTNode):
    name: str


def ast_to_dict(node: ASTNode) -> Any:
    if isinstance(node, Program):
        return {"type": "Program", "statements": [ast_to_dict(stmt) for stmt in node.statements]}
    if isinstance(node, Assignment):
        return {"type": "Assignment", "name": node.name, "expression": ast_to_dict(node.expression)}
    if isinstance(node, VarDeclaration):
        return {"type": "VarDeclaration", "name": node.name, "init": ast_to_dict(node.init) if node.init is not None else None}
    if isinstance(node, WhenStatement):
        return {
            "type": "WhenStatement",
            "condition": ast_to_dict(node.condition),
            "body": [ast_to_dict(stmt) for stmt in node.body],
        }
    if isinstance(node, PrintStatement):
        return {"type": "PrintStatement", "expression": ast_to_dict(node.expression)}
    if isinstance(node, AskStatement):
        return {"type": "AskStatement", "name": node.name, "prompt": ast_to_dict(node.prompt) if node.prompt is not None else None}
    if isinstance(node, LoopStatement):
        return {
            "type": "LoopStatement",
            "condition": ast_to_dict(node.condition),
            "body": [ast_to_dict(stmt) for stmt in node.body],
        }
    if isinstance(node, BinaryOperation):
        return {
            "type": "BinaryOperation",
            "operator": node.operator,
            "left": ast_to_dict(node.left),
            "right": ast_to_dict(node.right),
        }
    if isinstance(node, Number):
        return {"type": "Number", "value": node.value}
    if isinstance(node, String):
        return {"type": "String", "value": node.value}
    if isinstance(node, Boolean):
        return {"type": "Boolean", "value": node.value}
    if isinstance(node, Identifier):
        return {"type": "Identifier", "name": node.name}
    return {"type": node.__class__.__name__}
