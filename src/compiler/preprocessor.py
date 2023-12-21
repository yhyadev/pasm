from dataclasses import dataclass
from pathlib import Path
from .lexer import *
from .errors import Diagnoster, ErrorKind


@dataclass()
class Preprocessor:
    tokens: list[Token]
    included_files: list[Path]

    def preprocess_tokens(self) -> list[Token]:
        processed_tokens = []

        while len(self.tokens) > 0:
            match self.tokens.pop(0):
                case tok if tok.kind == TokenKind.Identifier and tok.value == "include":
                    processed_tokens.extend(self.include_file())
                case tok:
                    processed_tokens.append(tok)
                    continue

        return processed_tokens

    def include_file(self) -> list[Token]:
        if self.tokens[0].kind != TokenKind.String:
            self.tokens[0].diagnoster.error_panic(
                ErrorKind.Invalid, "syntax: expected the file path to be a string"
            )

        file_path = Path(self.tokens[0].value)

        if not file_path.exists() or not file_path.is_file():
            self.tokens[0].diagnoster.error_panic(
                ErrorKind.Invalid, f"include: {file_path} is not a file"
            )

        self.tokens.pop(0)

        if file_path in self.included_files:
            return []
        else:
            self.included_files.append(file_path)

        with open(file_path, "r") as f:
            lexer = Lexer(list(f.read()), Diagnoster(file_path))
            file_tokens = lexer.tokenize()
            file_tokens.pop()  # Pop the EOF Token

        file_tokens.extend(self.tokens)
        self.tokens = file_tokens

        return self.preprocess_tokens()
