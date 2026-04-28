from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Assignment, BinaryOperation, Identifier, Number, PrintStatement, Program, WhenStatement
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
        while self.match("NEWLINE"):
            self.advance()

    def parse(self) -> Program:
        statements = self.parse_statement_list()
        self.consume("EOF", "Expected end of file")
        return Program(statements)

    def parse_statement_list(self) -> list:
        statements = []
        self.skip_newlines()
        while not self.match("EOF") and not self.match("DEDENT"):
            statements.append(self.parse_statement())
            self.skip_newlines()
        return statements

    def parse_statement(self):
        if self.match("ID") and self.tokens[self.position + 1].type == "ARROW":
            return self.parse_assignment()
        if self.match("WHEN"):
            return self.parse_when()
        if self.match("SAY"):
            return self.parse_print()
        token = self.current()
        raise ParserError(f"Unexpected token {token.type} at line {token.line}, column {token.column}")

    def parse_assignment(self) -> Assignment:
        name = self.consume("ID", "Expected variable name").value
        self.consume("ARROW", "Expected '->' in assignment")
        expression = self.parse_expression()
        return Assignment(name=name or "", expression=expression)

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

    def parse_expression(self):
        node = self.parse_term()
        while self.match("OP") and self.current().value in {">", "<"}:
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
        node = self.parse_primary()
        while self.match("OP") and self.current().value in {"*", "/"}:
            operator = self.advance().value or ""
            right = self.parse_primary()
            node = BinaryOperation(left=node, operator=operator, right=right)
        return node

    def parse_primary(self):
        token = self.current()
        if token.type == "NUMBER":
            self.advance()
            return Number(int(token.value or "0"))
        if token.type == "ID":
            self.advance()
            return Identifier(token.value or "")
        raise ParserError(f"Expected a number or identifier at line {token.line}, column {token.column}")
