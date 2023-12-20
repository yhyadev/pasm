from dataclasses import dataclass
from .base import ASMBackend
from ..code import ASMInstruction, ASMReturn
from ...ir.code import *


@dataclass()
class Aarch64Backend(ASMBackend):
    def add_entry_point(self):
        self.code.text_segment += ".global _start\n"
        self.code.text_segment += "_start:\n"
        self.code.text_segment += "\tbl main\n"
        self.code.text_segment += "\tmov w8, #93\n"
        self.code.text_segment += "\tmov w0, wzr\n"
        self.code.text_segment += "\tsvc #0\n"
    
    def initialize_data_segment(self):
        for (i, string_literal) in enumerate(self.code.string_literals):
            self.code.data_segement += f"str{i}:\n"
            self.code.data_segement += f"\t.asciz \"{''.join(string_literal)}\"\n"

    def add_label_start(self, block: IRBlock):
        self.code.text_segment += f".global {block.name}\n"
        self.code.text_segment += f"{block.name}:\n"

    def add_label_end(self, block: IRBlock):
        if not block.returned and block.signature.return_type == Type.Void:
            self.add_instruction(ASMReturn())

    def add_instruction(self, instruction: ASMInstruction):
        self.code.text_segment += f"\t{instruction.to_aarch64()}\n"

    def add_string_literal(self, value: str):
        self.code.string_literals.append(list(value))

    def repr_register(self, number: int) -> str:
        return f"x{number}"

    def repr_integer(self, value: int) -> str:
        return f"#{value}"

    def repr_float(self, value: float) -> str:
        return f"#{value}"
    
    def display_code(self) -> str:
        result = ""

        result += ".text\n"
        result += "".join(self.code.text_segment)

        result += "\n"

        result += ".data\n"
        result += "".join(self.code.data_segement)

        return result
