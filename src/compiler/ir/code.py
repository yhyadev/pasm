from dataclasses import dataclass, field
from ..ast import Type
from ..errors import Diagnoster


class IRValue:
    def get_type(self) -> Type:
        return Type.Void

    def get_diagnoster(self) -> Diagnoster:
        ...


@dataclass()
class IRInteger(IRValue):
    value: int
    diagnoster: Diagnoster

    def get_type(self) -> Type:
        return Type.Integer

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class IRFloat(IRValue):
    value: float
    diagnoster: Diagnoster

    def get_type(self) -> Type:
        return Type.Float

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class IRStringLiteral:
    value: str


@dataclass()
class IRStringReference(IRValue):
    index: int
    diagnoster: Diagnoster

    def get_type(self) -> Type:
        return Type.String

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


class IRInstruction:
    def get_diagnoster(self) -> Diagnoster:
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
    diagnoster: Diagnoster

    def get_type(self) -> Type:
        return self.signature.return_type

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class IRCall(IRValue, IRInstruction):
    callable: IRBlockReference
    arguments: list[IRValue]

    def get_type(self) -> Type:
        return self.callable.signature.return_type

    def get_diagnoster(self) -> Diagnoster:
        return self.callable.get_diagnoster()


@dataclass()
class IRReturn(IRInstruction):
    value: IRValue
    diagnoster: Diagnoster

    def get_diagnoster(self) -> Diagnoster:
        return self.diagnoster


@dataclass()
class IRCode:
    diagnoster: Diagnoster
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
