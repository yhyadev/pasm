from dataclasses import dataclass
from .backends.base import ASMBackend, ASMInstruction
from .code import *
from ..errors import ErrorKind
from ..ir.code import *


@dataclass()
class ASMGen:
    backend: ASMBackend
    ir_code: IRCode

    def generate(self):
        if self.ir_code.get_block("main") == None:
            self.ir_code.diagnoster.error_panic(
                ErrorKind.Invalid, "program: main function is undefined"
            )

        self.backend.add_entry_point()

        for block in self.ir_code.blocks:
            self.backend.add_label_start(block)

            for instruction in block.instructions:
                self.backend.add_instruction(self.generate_asm_instruction(instruction))

            self.backend.add_label_end(block)

        for string_literal in self.ir_code.string_literals:
            self.backend.add_string_literal(string_literal.value)

        self.backend.initialize_data_segment()

    def generate_asm_instruction(self, instruction: IRInstruction) -> ASMInstruction:
        match instruction:
            case call if isinstance(call, IRCall):
                match call.callable:
                    case br if isinstance(br, IRBlockReference):
                        block = self.ir_code.blocks[br.index]

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
            case stringref if isinstance(stringref, IRStringReference):
                self.backend.add_instruction(ASMLoadAddress(0, f"str{stringref.index}"))
                return self.backend.repr_register(0)
            case call if isinstance(call, IRCall):
                self.backend.add_instruction(self.generate_asm_instruction(call))
                return self.backend.repr_register(0)
            case _:
                value.get_diagnoster().error_panic(ErrorKind.Invalid, "value")
