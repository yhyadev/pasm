from dataclasses import dataclass, field
from ..code import ASMCode, ASMInstruction
from ...ir.code import IRBlock, IRValue

@dataclass()
class ASMBackend:
    code: ASMCode = field(default_factory=ASMCode)

    def add_label_start(self, block: IRBlock):
        ...
    
    def add_label_end(self, block: IRBlock):
        ...
    
    def add_instruction(self, instruction: ASMInstruction):
        ...

    def display_code(self) -> str:
        ...
