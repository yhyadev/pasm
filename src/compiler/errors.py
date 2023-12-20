import enum
from dataclasses import dataclass, field
from sys import stderr
from pathlib import Path
from typing import Never
from .position import Position


class ErrorKind(enum.Enum):
    Invalid = enum.auto()
    Unspported = enum.auto()
    Unknown = enum.auto()
    Types = enum.auto()


@dataclass()
class Error:
    kind: ErrorKind
    context: str

    def panic(self, file_path: Path, position: Position) -> Never:
        print(
            f"{file_path}:{position}: {self.kind.name.lower()} {self.context}",
            file=stderr,
        )
        exit(self.kind.value)


@dataclass()
class Diagnoster:
    file_path: Path
    position: Position = field(default_factory=Position)

    def error_panic(self, kind: ErrorKind, context: str) -> Never:
        Error(kind, context).panic(self.file_path, self.position)
