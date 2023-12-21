from dataclasses import dataclass
import os
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

    def include_file_search(self, input_file: str) -> Path | None:
        if os.path.isfile(input_file) and os.path.exists(input_file):
            return Path(input_file)
        else:
            pasmlib_paths = [
                Path(os.environ.get("PREFIX", "") + "/lib/pasm"),
                Path("../pasm/lib"),
                Path("./lib"),
                Path("../lib"),
            ]

            for pasmlib_path in pasmlib_paths:
                pasmlib_path = pasmlib_path.joinpath(input_file)

                if pasmlib_path.exists() and pasmlib_path.is_file():
                    return pasmlib_path

        return None

    def include_file(self) -> list[Token]:
        if self.tokens[0].kind != TokenKind.String or len(self.tokens[0].value) == 0:
            self.tokens[0].diagnoster.error_panic(
                ErrorKind.Invalid,
                "syntax: expected the file path to be a non-empty string",
            )

        file_path = self.include_file_search(self.tokens[0].value)

        if file_path == None:
            self.tokens[0].diagnoster.error_panic(
                ErrorKind.Invalid, f"include: {self.tokens[0].value} is not a file"
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
