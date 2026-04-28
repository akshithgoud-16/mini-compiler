from __future__ import annotations

from dataclasses import dataclass

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
from .tokens import Token


class ParserError(Exception):
    pass


@dataclass
class Parser:
    tokens: list[Token]

    def __post_init__(self) -> None:
        self.position = 0

    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> Token:
        token = self.current()
        if token.type != "EOF":
            self.position += 1
        return token

    def match(self, *token_types: str) -> bool:
        return self.current().type in token_types

    def consume(self, token_type: str, message: str) -> Token:
        if self.match(token_type):
            return self.advance()
        token = self.current()
        raise ParserError(f"{message} at line {token.line}, column {token.column}")

    def skip_newlines(self) -> None:
        while self.match("NEWLINE", "STOP"):
            self.advance()

    def parse(self) -> Program:
        # allow optional START/END markers
        if self.match("START"):
            self.advance()
        statements = self.parse_statement_list()
        if self.match("END"):
            self.advance()
        self.skip_newlines()
        self.consume("EOF", "Expected end of file")
        return Program(statements)

    def parse_statement_list(self) -> list:
        statements = []
        self.skip_newlines()
        while not self.match("EOF") and not self.match("DEDENT") and not self.match("END"):
            statements.append(self.parse_statement())
            self.skip_newlines()
        return statements

    def parse_statement(self):
        if self.match("NUMBER_KW"):
            return self.parse_declaration()
        if self.match("ASK"):
            return self.parse_ask()
        if self.match("ID") and self.tokens[self.position + 1].type == "ARROW":
            return self.parse_assignment()
        if self.match("WHEN"):
            return self.parse_when()
        if self.match("LOOP"):
            return self.parse_loop()
        if self.match("SAY"):
            return self.parse_print()
        token = self.current()
        raise ParserError(f"Unexpected token {token.type} at line {token.line}, column {token.column}")

    def parse_assignment(self) -> Assignment:
        name = self.consume("ID", "Expected variable name").value
        self.consume("ARROW", "Expected '->' in assignment")
        expression = self.parse_expression()
        return Assignment(name=name or "", expression=expression)

    def parse_declaration(self) -> VarDeclaration:
        # 'number x' [-> expr]
        self.consume("NUMBER_KW", "Expected 'number' keyword")
        name = self.consume("ID", "Expected variable name").value
        init = None
        if self.match("ARROW"):
            self.advance()
            init = self.parse_expression()
        return VarDeclaration(name=name or "", init=init)

    def parse_loop(self) -> LoopStatement:
        self.consume("LOOP", "Expected 'loop'")
        condition = self.parse_expression()
        self.consume("COLON", "Expected ':' after loop condition")
        self.skip_newlines()
        body = [self.parse_statement()]
        return LoopStatement(condition=condition, body=body)

    def parse_when(self) -> WhenStatement:
        self.consume("WHEN", "Expected 'when'")
        condition = self.parse_expression()
        self.consume("COLON", "Expected ':' after when condition")
        self.skip_newlines()
        body = [self.parse_statement()]
        return WhenStatement(condition=condition, body=body)

    def parse_print(self) -> PrintStatement:
        self.consume("SAY", "Expected 'say'")
        expression = self.parse_expression()
        return PrintStatement(expression=expression)

    def parse_ask(self) -> "AskStatement":
        from .ast_nodes import AskStatement

        self.consume("ASK", "Expected 'ask'")
        prompt = None
        # allow: ask "prompt" -> var   OR   ask var
        if self.match("STRING"):
            prompt = self.parse_primary()
            if self.match("ARROW"):
                self.advance()
                name = self.consume("ID", "Expected variable name after '->'").value
                return AskStatement(name=name or "", prompt=prompt)
            # otherwise consume identifier next
        if self.match("ID"):
            name = self.consume("ID", "Expected variable name").value
            return AskStatement(name=name or "", prompt=prompt)
        raise ParserError("Invalid ask statement syntax")

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.match("OP") and self.current().value == "||":
            op = self.advance().value or ""
            right = self.parse_and()
            node = BinaryOperation(left=node, operator=op, right=right)
        return node

    def parse_and(self):
        node = self.parse_comparison()
        while self.match("OP") and self.current().value == "&&":
            op = self.advance().value or ""
            right = self.parse_comparison()
            node = BinaryOperation(left=node, operator=op, right=right)
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.match("OP") and self.current().value in {">", "<", ">=", "<=", "==", "!="}:
            operator = self.advance().value or ""
            right = self.parse_term()
            node = BinaryOperation(left=node, operator=operator, right=right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.match("OP") and self.current().value in {"+", "-"}:
            operator = self.advance().value or ""
            right = self.parse_factor()
            node = BinaryOperation(left=node, operator=operator, right=right)
        return node

    def parse_factor(self):
        node = self.parse_unary()
        while self.match("OP") and self.current().value in {"*", "/", "%", "**"}:
            operator = self.advance().value or ""
            right = self.parse_unary()
            node = BinaryOperation(left=node, operator=operator, right=right)
        return node

    def parse_unary(self):
        if self.match("OP") and self.current().value in {"-", "!"}:
            operator = self.advance().value or ""
            operand = self.parse_unary()
            # represent unary minus as binary with 0 left
            if operator == "-":
                return BinaryOperation(left=Number(0), operator="-", right=operand)
            # logical not will be represented as comparison to false
            if operator == "!":
                return BinaryOperation(left=operand, operator="==", right=Boolean(False))
        return self.parse_primary()

    def parse_primary(self):
        token = self.current()
        if token.type == "NUMBER":
            self.advance()
            return Number(int(token.value or "0"))
        if token.type == "STRING":
            self.advance()
            return String(token.value or "")
        if token.type == "TRUE":
            self.advance()
            return Boolean(True)
        if token.type == "FALSE":
            self.advance()
            return Boolean(False)
        if token.type == "ID":
            self.advance()
            return Identifier(token.value or "")
        raise ParserError(f"Expected a number, string, boolean, or identifier at line {token.line}, column {token.column}")
