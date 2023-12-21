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


class ASMBinaryOeration(ASMInstruction):
    instruction: str
    isfloat: bool
    out_reg: str
    lhs_reg: str
    rhs_reg: str

    def to_aarch64(self) -> str:
        if self.isfloat:
            self.instruction = "f" + self.instruction

        return f"{self.instruction} {self.out_reg}, {self.lhs_reg}, {self.rhs_reg}"


@dataclass()
class ASMAdd(ASMBinaryOeration):
    isfloat: bool
    out_reg: str
    lhs_reg: str
    rhs_reg: str
    instruction: str = "add"


@dataclass()
class ASMSub(ASMBinaryOeration):
    isfloat: bool
    out_reg: str
    lhs_reg: str
    rhs_reg: str
    instruction: str = "sub"


@dataclass()
class ASMMul(ASMBinaryOeration):
    isfloat: bool
    out_reg: str
    lhs_reg: str
    rhs_reg: str
    instruction: str = "mul"


@dataclass()
class ASMDiv(ASMBinaryOeration):
    isfloat: bool
    out_reg: str
    lhs_reg: str
    rhs_reg: str
    instruction: str = "div"


@dataclass()
class ASMCode:
    text_segment: list[str] = field(default_factory=list)
    data_segement: list[str] = field(default_factory=list)
    string_literals: list[list[str]] = field(default_factory=list)
