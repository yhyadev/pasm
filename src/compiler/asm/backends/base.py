from dataclasses import dataclass, field
from ..code import ASMCode, ASMInstruction
from ...ir.code import IRBlock, IRValue


@dataclass()
class ASMBackend:
    code: ASMCode = field(default_factory=ASMCode)

    def add_entry_point(self):
        ...

    def initialize_data_segment(self):
        ...

    def add_label_start(self, block: IRBlock):
        ...

    def add_label_end(self, block: IRBlock):
        ...

    def add_instruction(self, instruction: ASMInstruction):
        ...

    def add_string_literal(self, value: str):
        ...

    def repr_register(self, number: int) -> str:
        ...

    def repr_integer(self, value: int) -> str:
        ...

    def repr_float(self, value: float) -> str:
        ...

    def ref_string(self, index: int) -> str:
        ...

    def display_code(self) -> str:
        ...
