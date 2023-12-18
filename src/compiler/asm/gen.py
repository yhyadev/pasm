import sys
from dataclasses import dataclass
from .backends.base import ASMBackend, ASMInstruction
from .code import *
from ..ir.code import *

@dataclass()
class ASMGen():
    backend: ASMBackend
    ircode: IRCode

    def generate(self):
        if self.ircode.get_block("main") == None:
            print("expected a main function", file=sys.stderr)
            exit(1)

        self.backend.add_entry_point()

        for block in self.ircode.blocks:
            self.backend.add_label_start(block)

            for instruction in block.instructions:
                self.backend.add_instruction(self.generate_asm_instruction(instruction))

            self.backend.add_label_end(block)

    def generate_asm_instruction(self, instruction: IRInstruction) -> ASMInstruction:
        match instruction:
            case call if isinstance(call, IRCall):
                match call.callable:
                    case br if isinstance(br, IRBlockReference):
                        block = self.ircode.blocks[br.index]
                        
                        if len(call.arguments) != len(block.signature.parameters_types):
                            print(f"expected {len(block.signature.parameters_types)} arguments got {len(call.arguments)}", file=sys.stderr)
                            exit(1)

                        for (i, parameter_type) in enumerate(block.signature.parameters_types):
                            if call.arguments[i].get_type() != parameter_type:
                                print("mismatched types in call", file=sys.stderr)
                                exit(1)

                        for (i, argument) in enumerate(call.arguments):
                            self.backend.add_instruction(ASMMove(i, self.generate_value(argument)))

                        return ASMCall(block.name)
                    case _:
                        print("callable is not handled", file=sys.stderr)
                        exit(1)
            case ret if isinstance(ret, IRReturn):
                self.backend.add_instruction(ASMMove(0, self.generate_value(ret.value)))
                
                return ASMReturn()
            case _:
                print("instruction is unimplemented yet", file=sys.stderr)
                exit(1)

    def generate_value(self, value: IRValue) -> str:
        match value:
            case integer if isinstance(integer, IRInteger):
                return f"#{integer.value}"
            case call if isinstance(call, IRCall):
                self.backend.add_instruction(self.generate_asm_instruction(call))
                return "x0"
            case _:
                print("value is not handled yet", file=sys.stderr)
                exit(1)
