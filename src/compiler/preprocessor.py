import os
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

    def find_include_file(self, file_path: Path) -> Path | None:
        if file_path.is_file():
            return file_path

        pasmlib_paths = [
            Path(os.environ.get("PREFIX", "") + "/lib/pasm"),
            Path(os.environ.get("PATH", "") + "/pasm/lib"),
            Path("~/pasm/lib").expanduser(),
            Path("./lib"),
            Path("../lib"),
        ]

        for pasmlib_path in pasmlib_paths:
            combined_path = pasmlib_path.joinpath(file_path)

            if combined_path.is_file():
                return combined_path

        return None

    def include_file(self) -> list[Token]:
        if self.tokens[0].kind != TokenKind.String or len(self.tokens[0].value) == 0:
            self.tokens[0].diagnoster.error_panic(
                ErrorKind.Invalid,
                "syntax: expected the file path to be a non-empty string",
            )

        file_path = self.find_include_file(
            self.included_files[-1].parent.joinpath(self.tokens[0].value)
        )

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
