from dataclasses import dataclass
import enum

from compiler.errors import Diagnoster
from .lexer import Token


class Type(enum.Enum):
    Void = enum.auto()
    Integer = enum.auto()
    Float = enum.auto()
    String = enum.auto()

    def __str__(self) -> str:
        return self.name.lower()


class Node(object):
    ...


class Statement(Node):
    def get_diagnoster(self) -> Diagnoster:
        ...


class Expression(Statement):
    ...


@dataclass()
class Identifier(Expression):
    value: str
    diagnoster: Diagnoster

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class String(Expression):
    value: str
    diagnoster: Diagnoster

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class Integer(Expression):
    value: int
    diagnoster: Diagnoster

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class Float(Expression):
    value: float
    diagnoster: Diagnoster

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class BinaryOperation(Expression):
    lhs: Expression
    operator: Token
    rhs: Expression

    def get_diagnoster(self) -> Diagnoster:
        return self.operator.diagnoster


@dataclass()
class Call(Expression):
    callable: Expression
    arguments: list[Expression]

    def get_diagnoster(self) -> Diagnoster:
        return self.callable.get_diagnoster()


@dataclass()
class FunctionParameter:
    name: Identifier
    expected_type: Type
    diagnoster: Diagnoster


@dataclass()
class FunctionDefinition(Statement):
    name: Identifier
    parameters: list[FunctionParameter]
    body: list[Statement]
    return_type: Type

    def get_diagnoster(self) -> Diagnoster:
        return self.name.get_diagnoster()


@dataclass()
class ReturnStatement(Statement):
    value: Expression

    def get_diagnoster(self) -> Diagnoster:
        return self.value.get_diagnoster()


@dataclass()
class Program(Node):
    body: list[Statement]
    diagnoster: Diagnoster
