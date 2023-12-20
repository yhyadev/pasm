from dataclasses import dataclass
from .backends.base import ASMBackend, ASMInstruction
from .code import *
from ..errors import ErrorKind
from ..ir.code import *


@dataclass()
class ASMGen:
    backend: ASMBackend
    ircode: IRCode

    def generate(self):
        if self.ircode.get_block("main") == None:
            self.ircode.diagnoster.error_panic(
                ErrorKind.Invalid, "program: main function is undefined"
            )

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
                            call.get_diagnoster().error_panic(
                                ErrorKind.Invalid,
                                f"call: expected {len(block.signature.parameters_types)} {'arguments' if len(block.signature.parameters_types) != 1 else 'argument'} got {len(call.arguments)}",
                            )

                        for i, parameter_type in enumerate(
                            block.signature.parameters_types
                        ):
                            if call.arguments[i].get_type() != parameter_type:
                                call.get_diagnoster().error_panic(
                                    ErrorKind.Types,
                                    f"mismatched: expected argument at position {i} to be of type {parameter_type} but got argument of type {call.arguments[i].get_type()}",
                                )

                        for i, argument in enumerate(call.arguments):
                            self.backend.add_instruction(
                                ASMMove(i, self.generate_value(argument))
                            )

                        return ASMCall(block.name)
                    case _:
                        call.get_diagnoster().error_panic(ErrorKind.Invalid, "callable")
            case ret if isinstance(ret, IRReturn):
                self.backend.add_instruction(ASMMove(0, self.generate_value(ret.value)))

                return ASMReturn()
            case _:
                instruction.get_diagnoster().error_panic(
                    ErrorKind.Invalid, "instruction"
                )

    def generate_value(self, value: IRValue) -> str:
        match value:
            case integer if isinstance(integer, IRInteger):
                return self.backend.repr_integer(integer.value)
            case floatv if isinstance(floatv, IRFloat):
                return self.backend.repr_float(floatv.value)
            case call if isinstance(call, IRCall):
                self.backend.add_instruction(self.generate_asm_instruction(call))
                return self.backend.repr_register(0)
            case _:
                value.get_diagnoster().error_panic(ErrorKind.Invalid, "value")
