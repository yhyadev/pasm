from dataclasses import dataclass
import enum
import sys
from typing import Any


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
    Percent = enum.auto()

    EOF = enum.auto()


@dataclass()
class Token:
    kind: TokenKind
    value: Any = ""


@dataclass()
class Lexer:
    chars: list[str]

    def tokenize(self) -> list[Token]:
        tokens = []

        while len(self.chars) != 0:
            match self.chars.pop(0):
                case "(":
                    tokens.append(Token(TokenKind.OpenParen))
                case ")":
                    tokens.append(Token(TokenKind.CloseParen))
                case "{":
                    tokens.append(Token(TokenKind.OpenBrace))
                case "}":
                    tokens.append(Token(TokenKind.CloseBrace))
                case ":":
                    tokens.append(Token(TokenKind.Colon))
                case ".":
                    tokens.append(Token(TokenKind.Period))
                case ",":
                    tokens.append(Token(TokenKind.Comma))
                case "+":
                    tokens.append(Token(TokenKind.Plus))
                case "-":
                    tokens.append(Token(TokenKind.Minus))
                case "*":
                    tokens.append(Token(TokenKind.Star))
                case "/":
                    tokens.append(Token(TokenKind.ForwardSlash))
                case "%":
                    tokens.append(Token(TokenKind.Percent))
                case '"':
                    tokens.append(self.read_string())
                case c if c.isdigit():
                    tokens.append(self.read_number(c))
                case c if c.isalpha() or c == "_":
                    tokens.append(self.read_ident(c))
                case c if c.isspace():
                    continue
                case c:
                    print(f"invalid token '{c}'", file=sys.stderr)
                    exit(1)

        tokens.append(Token(TokenKind.EOF))

        return tokens

    def read_string(self) -> Token:
        literal = ""

        while True:
            c = self.chars.pop(0)

            if c == '"':
                break

            literal += c

        return Token(TokenKind.String, literal)

    def read_number(self, first_char: str) -> Token:
        literal = first_char

        while True:
            c = self.chars[0]

            if c.isdigit() or c == ".":
                literal += self.chars.pop(0)
            else:
                break

        if "." in literal:
            return Token(TokenKind.Float, float(literal))
        else:
            return Token(TokenKind.Integer, int(literal))

    def read_ident(self, first_char: str) -> Token:
        literal = first_char

        while True:
            c = self.chars[0]

            if c.isalnum() or c == "_":
                literal += self.chars.pop(0)
            else:
                break

        return Token(TokenKind.Identifier, literal)
