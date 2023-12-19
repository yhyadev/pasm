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
    register_number: int
    value: str

    def to_aarch64(self) -> str:
        if "." in self.value:
            instruction = "fmov"
            register_type = "d"
        else:
            instruction = "mov"
            register_type = "x"

        return f"{instruction} {register_type}{self.register_number}, {self.value}"

@dataclass()
class ASMLoadAddress(ASMInstruction):
    register_number: int
    address: str

    def to_aarch64(self) -> str:
        return f"adr x{self.register_number}, {self.address}"
    

@dataclass()
class ASMCode:
    lines: list[str] = field(default_factory=list)
    data_segement: list[str] = field(default_factory=list)
    string_literals: list[str] = field(default_factory=list)
