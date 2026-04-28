from __future__ import annotations

from dataclasses import dataclass

from .ir import IRInstruction, IRProgram


@dataclass
class Optimizer:
    """Apply small local optimizations such as constant folding."""

    def optimize(self, ir_program: IRProgram) -> IRProgram:
        optimized: list[IRInstruction] = []

        for instruction in ir_program.instructions:
            if instruction.op == "BINARY" and instruction.arg1 is not None and instruction.arg2 is not None:
                operator, right_operand = instruction.arg2.split(" ", 1)
                if instruction.arg1.isdigit() and right_operand.isdigit():
                    left_value = int(instruction.arg1)
                    right_value = int(right_operand)
                    result = self.fold_constants(left_value, operator, right_value)
                    optimized.append(IRInstruction(op="ASSIGN", result=instruction.result, arg1=str(result)))
                    continue
            optimized.append(instruction)

        return IRProgram(optimized)

    def fold_constants(self, left: int, operator: str, right: int) -> int:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise ZeroDivisionError("Division by zero during constant folding")
            return left // right
        if operator == ">":
            return int(left > right)
        if operator == "<":
            return int(left < right)
        raise ValueError(f"Unsupported operator '{operator}'")
