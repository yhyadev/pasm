from dataclasses import dataclass
from .base import ASMBackend
from ..code import ASMInstruction, ASMReturn
from ...ir.code import *

@dataclass()
class Aarch64Backend(ASMBackend):
    def add_entry_point(self):
        self.code.lines += "\t.global _start\n"
        self.code.lines += "_start:\n"
        self.code.lines += "\tbl main\n"
        self.code.lines += "\tmov w8, #93\n"
        self.code.lines += "\tmov w0, wzr\n"
        self.code.lines += "\tsvc #0\n"
    
    def add_label_start(self, block: IRBlock):
        self.code.lines += f"\t.global {block.name}\n"
        self.code.lines += f"{block.name}:\n"
    
    def add_label_end(self, block: IRBlock):
        if not block.returned and block.signature.return_type == Type.Void:
            self.add_instruction(ASMReturn())
    
    def add_instruction(self, instruction: ASMInstruction):
        self.code.lines += f"\t{instruction.to_aarch64()}\n"
    
    def repr_register(self, number: int) -> str:
        return f"x{number}"
    
    def repr_integer(self, value: int) -> str:
        return f"#{value}"
    
    def repr_float(self, value: float) -> str:
        return f"#{value}"

    def display_code(self) -> str:
        return "".join(self.code.lines)
