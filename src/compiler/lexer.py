from dataclasses import dataclass
import enum
from typing import Any
from copy import deepcopy
from .errors import Diagnoster, ErrorKind


class TokenKind(enum.Enum):
    Identifier = enum.auto()
    String = enum.auto()
    Integer = enum.auto()
    Float = enum.auto()

    OpenParen = enum.auto()
    CloseParen = enum.auto()
    OpenBrace = enum.auto()
    CloseBrace = enum.auto()

    Colon = enum.auto()
    Period = enum.auto()
    Comma = enum.auto()

    Plus = enum.auto()
    Minus = enum.auto()
    Star = enum.auto()
    ForwardSlash = enum.auto()

    EOF = enum.auto()


@dataclass()
class Token:
    diagnoster: Diagnoster
    kind: TokenKind
    value: Any = ""


@dataclass()
class Lexer:
    chars: list[str]
    diagnoster: Diagnoster

    def tokenize(self) -> list[Token]:
        tokens = []

        while len(self.chars) != 0:
            match self.chars.pop(0):
                case "(":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.OpenParen))
                case ")":
                    tokens.append(
                        Token(deepcopy(self.diagnoster), TokenKind.CloseParen)
                    )
                case "{":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.OpenBrace))
                case "}":
                    tokens.append(
                        Token(deepcopy(self.diagnoster), TokenKind.CloseBrace)
                    )
                case ":":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.Colon))
                case ".":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.Period))
                case ",":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.Comma))
                case "+":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.Plus))
                case "-":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.Minus))
                case "*":
                    tokens.append(Token(deepcopy(self.diagnoster), TokenKind.Star))
                case "/":
                    tokens.append(
                        Token(deepcopy(self.diagnoster), TokenKind.ForwardSlash)
                    )
                case '"':
                    tokens.append(self.read_string())
                case c if c.isdigit():
                    tokens.append(self.read_number(c))
                case c if c.isalpha() or c == "_":
                    tokens.append(self.read_ident(c))
                case c if c.isspace():
                    if c == "\n":
                        self.diagnoster.position.line += 1
                        self.diagnoster.position.column = 1
                    continue
                case c:
                    self.diagnoster.error_panic(ErrorKind.Invalid, f"token '{c}'")

            self.diagnoster.position.column += 1

        tokens.append(Token(deepcopy(self.diagnoster), TokenKind.EOF))

        return tokens

    def read_string(self) -> Token:
        literal = ""

        while True:
            c = self.chars.pop(0)

            if c == '"':
                break

            literal += c

        return Token(deepcopy(self.diagnoster), TokenKind.String, literal)

    def read_number(self, first_char: str) -> Token:
        literal = first_char

        while True:
            c = self.chars[0]

            if c.isdigit() or c == ".":
                literal += self.chars.pop(0)
            else:
                break

        if "." in literal:
            return Token(deepcopy(self.diagnoster), TokenKind.Float, float(literal))
        else:
            return Token(deepcopy(self.diagnoster), TokenKind.Integer, int(literal))

    def read_ident(self, first_char: str) -> Token:
        literal = first_char

        while True:
            c = self.chars[0]

            if c.isalnum() or c == "_":
                literal += self.chars.pop(0)
            else:
                break

        return Token(deepcopy(self.diagnoster), TokenKind.Identifier, literal)
