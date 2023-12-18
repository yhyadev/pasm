from dataclasses import dataclass, field
from ..ir.code import *

class ASMInstruction:
    def to_aarch64(self) -> str:
        ...

@dataclass()
class ASMCall(ASMInstruction):
    label_name: str

    def to_aarch64(self) -> str:
        return f"bl {self.label_name}"

@dataclass()
class ASMReturn(ASMInstruction):
    def to_aarch64(self) -> str:
        return "ret"

@dataclass()
class ASMMove(ASMInstruction):
    register: int
    value: str

    def to_aarch64(self) -> str:
        return f"mov x{self.register}, {self.value}"

@dataclass()
class ASMLoadAddress(ASMInstruction):
    register: int
    address: str

    def to_aarch64(self) -> str:
        return f"adr x{self.register}, {self.address}"
    

@dataclass()
class ASMCode:
    lines: list[str] = field(default_factory=list)
    data_segement: list[str] = field(default_factory=list)
    string_literals: list[str] = field(default_factory=list)
