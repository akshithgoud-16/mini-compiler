from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import Assignment, BinaryOperation, Identifier, Number, PrintStatement, Program, WhenStatement


@dataclass
class IRInstruction:
    op: str
    result: str | None = None
    arg1: str | None = None
    arg2: str | None = None
    label: str | None = None

    def __str__(self) -> str:
        if self.op == "LABEL":
            return f"{self.label}:"
        if self.op == "GOTO":
            return f"goto {self.label}"
        if self.op == "IF_GOTO":
            return f"if {self.arg1} goto {self.label}"
        if self.op == "PRINT":
            return f"print {self.arg1}"
        if self.op == "ASSIGN":
            return f"{self.result} = {self.arg1}"
        if self.op == "BINARY":
            return f"{self.result} = {self.arg1} {self.arg2}"
        return self.op


@dataclass
class IRProgram:
    instructions: list[IRInstruction] = field(default_factory=list)

    def __str__(self) -> str:
        return "\n".join(str(instruction) for instruction in self.instructions)


class IRGenerator:
    def __init__(self):
        self.instructions: list[IRInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self, program: Program) -> IRProgram:
        for statement in program.statements:
            self.emit_statement(statement)
        return IRProgram(self.instructions)

    def emit_statement(self, node) -> None:
        if isinstance(node, Assignment):
            value = self.emit_expression(node.expression)
            self.instructions.append(IRInstruction(op="ASSIGN", result=node.name, arg1=value))
            return
        if isinstance(node, PrintStatement):
            value = self.emit_expression(node.expression)
            self.instructions.append(IRInstruction(op="PRINT", arg1=value))
            return
        if isinstance(node, WhenStatement):
            condition_value = self.emit_expression(node.condition)
            true_label = self.new_label()
            end_label = self.new_label()
            self.instructions.append(IRInstruction(op="IF_GOTO", arg1=condition_value, label=true_label))
            self.instructions.append(IRInstruction(op="GOTO", label=end_label))
            self.instructions.append(IRInstruction(op="LABEL", label=true_label))
            for statement in node.body:
                self.emit_statement(statement)
            self.instructions.append(IRInstruction(op="LABEL", label=end_label))
            return
        raise TypeError(f"Unsupported AST node: {node.__class__.__name__}")

    def emit_expression(self, node) -> str:
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, BinaryOperation):
            left = self.emit_expression(node.left)
            right = self.emit_expression(node.right)
            temp = self.new_temp()
            self.instructions.append(IRInstruction(op="BINARY", result=temp, arg1=left, arg2=f"{node.operator} {right}"))
            return temp
        raise TypeError(f"Unsupported expression node: {node.__class__.__name__}")
