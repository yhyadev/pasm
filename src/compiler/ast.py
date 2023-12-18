from dataclasses import dataclass
import enum
from .lexer import Token

class Type(enum.Enum):
    Void = enum.auto()
    Integer = enum.auto()
    Float = enum.auto()
    String = enum.auto()

class Node(object):
    ...

class Statement(Node):
    ...

class Expression(Statement):
    ...

@dataclass()
class Identifier(Expression):
    value: str

@dataclass()
class String(Expression):
    value: str

@dataclass()
class Integer(Expression):
    value: int

@dataclass()
class Float(Expression):
    value: float

@dataclass()
class BinaryOperation(Expression):
    lhs: Expression
    operator: Token
    rhs: Expression
 
@dataclass()
class Call(Expression):
    callable: Expression
    arguments: list[Expression]

@dataclass()
class FunctionParameter:
    name: Identifier
    expected_type: Type

@dataclass()
class FunctionDefinition(Statement):
    name: Identifier
    parameters: list[FunctionParameter]
    body: list[Statement]
    return_type: Type

@dataclass()
class ReturnStatement(Statement):
    value: Expression

@dataclass()
class Program(Node):
    body: list[Statement]
