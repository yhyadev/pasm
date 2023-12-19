from dataclasses import dataclass, field
from ..ast import Type

class IRValue:
    def get_type(self) -> Type:
        return Type.Void

@dataclass()
class IRInteger(IRValue):
    value: int

    def get_type(self) -> Type:
        return Type.Integer

@dataclass()
class IRFloat(IRValue):
    value: float
    
    def get_type(self) -> Type:
        return Type.Float

@dataclass()
class IRStringLiteral():
    value: str

@dataclass()
class IRStringReference(IRValue):
    index: int
    
    def get_type(self) -> Type:
        return Type.String

class IRInstruction:
    ...

@dataclass()
class IRBlockSignature:
    parameters_types: list[Type]
    return_type: Type

@dataclass()
class IRBlock:
    name: str
    signature: IRBlockSignature
    instructions: list[IRInstruction] = field(default_factory=list)
    returned: bool = False

@dataclass()
class IRBlockReference(IRValue):
    index: int
    signature: IRBlockSignature

    def get_type(self) -> Type:
        return self.signature.return_type

@dataclass()
class IRCall(IRValue, IRInstruction):
    callable: IRBlockReference
    arguments: list[IRValue]

    def get_type(self) -> Type:
        return self.callable.signature.return_type

@dataclass()
class IRReturn(IRInstruction):
    value: IRValue

@dataclass()
class IRCode:
    blocks: list[IRBlock] = field(default_factory=list)
    string_literals: list[IRStringLiteral] = field(default_factory=list)

    def get_block(self, name: str) -> int | None:
        try:
            return [block.name for block in self.blocks].index(name)
        except ValueError:
            return None

    def add_string_literal(self, literal: IRStringLiteral) -> int:
        self.string_literals.append(literal)

        return len(self.string_literals) - 1
