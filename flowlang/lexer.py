from __future__ import annotations

import re

from .tokens import KEYWORDS, Token


class LexerError(Exception):
    pass


class Lexer:
    """Turn source text into a token stream using regular expressions."""

    token_specification = [
        ("NUMBER", r"\d+"),
        ("ARROW", r"->"),
        ("OP", r"[+\-*/><]"),
        ("COLON", r":"),
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t]+"),
        ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("MISMATCH", r".")
    ]

    def __init__(self, source: str):
        self.source = source
        self.regex = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in self.token_specification))

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        line = 1
        line_start = 0

        for match in self.regex.finditer(self.source):
            kind = match.lastgroup or "MISMATCH"
            value = match.group()
            column = match.start() - line_start + 1

            if kind == "NUMBER":
                tokens.append(Token("NUMBER", value, line, column))
            elif kind == "ARROW":
                tokens.append(Token("ARROW", value, line, column))
            elif kind == "OP":
                tokens.append(Token("OP", value, line, column))
            elif kind == "COLON":
                tokens.append(Token("COLON", value, line, column))
            elif kind == "NEWLINE":
                tokens.append(Token("NEWLINE", None, line, column))
                line += 1
                line_start = match.end()
            elif kind == "SKIP":
                continue
            elif kind == "ID":
                token_type = KEYWORDS.get(value, "ID")
                tokens.append(Token(token_type, value, line, column))
            else:
                raise LexerError(f"Unexpected character {value!r} at line {line}, column {column}")

        tokens.append(Token("EOF", None, line, len(self.source) - line_start + 1))
        return tokens
