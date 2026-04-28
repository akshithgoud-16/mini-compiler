from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    type: str
    value: str | None
    line: int
    column: int

    def __str__(self) -> str:
        if self.value is None:
            return f"{self.type}({self.line}:{self.column})"
        return f"{self.type}({self.value!r}@{self.line}:{self.column})"


KEYWORDS = {
    "when": "WHEN",
    "say": "SAY",
    "START": "START",
    "END": "END",
    "number": "NUMBER_KW",
    "stop": "STOP",
    "ask": "ASK",
    "loop": "LOOP",
    "true": "TRUE",
    "false": "FALSE",
}
