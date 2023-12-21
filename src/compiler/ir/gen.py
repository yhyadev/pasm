from dataclasses import dataclass
from ..errors import ErrorKind
from .code import *
from ..ast import *


@dataclass
class IRGen:
    program: Program
    code: IRCode
    current_block: IRBlock | None

    def __init__(self, program: Program) -> None:
        self.program = program
        self.code = IRCode(program.diagnoster)
        self.current_block = None

    def generate(self):
        for stmt in self.program.body:
            self.generate_stmt(stmt)

    def generate_stmt(self, stmt: Statement):
        match stmt:
            case funcdef if isinstance(funcdef, FunctionDefinition):
                if self.code.get_block(funcdef.name.value) != None:
                    funcdef.name.diagnoster.error_panic(
                        ErrorKind.Invalid, "function: function name is already used"
                    )

                if self.current_block != None:
                    funcdef.get_diagnoster().error_panic(
                        ErrorKind.Invalid,
                        "function: function cannot be defined inside another function",
                    )

                self.current_block = IRBlock(
                    funcdef.name.value,
                    IRBlockSignature(
                        [parameter.expected_type for parameter in funcdef.parameters],
                        funcdef.return_type,
                    ),
                )

                for stmt in funcdef.body:
                    self.generate_stmt(stmt)

                if (
                    not self.current_block.returned
                    and self.current_block.signature.return_type != Type.Void
                ):
                    funcdef.get_diagnoster().error_panic(
                        ErrorKind.Invalid,
                        f"function: expected to return an expression with a type of {str(self.current_block.signature.return_type)}",
                    )

                self.code.blocks.append(self.current_block)
                self.current_block = None
            case returnstmt if isinstance(returnstmt, ReturnStatement):
                if self.current_block == None:
                    returnstmt.get_diagnoster().error_panic(
                        ErrorKind.Invalid,
                        "return statement: return statement must be in a function",
                    )

                value = self.generate_expr(returnstmt.value)

                if self.current_block.signature.return_type == Type.Void:
                    returnstmt.get_diagnoster().error_panic(
                        ErrorKind.Invalid,
                        "return statement: the function return type is void",
                    )

                if value.get_type() != self.current_block.signature.return_type:
                    returnstmt.get_diagnoster().error_panic(
                        ErrorKind.Types,
                        f"mismatched: expected the return value to be of type {str(self.current_block.signature.return_type)} but got a value of type {str(value.get_type())}",
                    )

                self.current_block.instructions.append(
                    IRReturn(value, returnstmt.get_diagnoster())
                )
                self.current_block.returned = True

            case expr if isinstance(expr, Expression):
                value = self.generate_expr(expr)

                if isinstance(value, IRInstruction):
                    assert self.current_block != None
                    self.current_block.instructions.append(value)
            case _:
                ...

    def generate_expr(self, expr: Expression) -> IRValue:
        if self.current_block == None:
            expr.get_diagnoster().error_panic(
                ErrorKind.Invalid,
                "expression: expected the expression to be inside a function",
            )

        match expr:
            case integerexpr if isinstance(integerexpr, Integer):
                return IRInteger(integerexpr.value, integerexpr.diagnoster)
            case floatexpr if isinstance(floatexpr, Float):
                return IRFloat(floatexpr.value, floatexpr.diagnoster)
            case stringexpr if isinstance(stringexpr, String):
                index = self.code.add_string_literal(IRStringLiteral(stringexpr.value))
                return IRStringReference(index, stringexpr.diagnoster)
            case callexpr if isinstance(callexpr, Call):
                match callexpr.callable:
                    case ident if isinstance(ident, Identifier):
                        block_index = self.code.get_block(ident.value)
                        if block_index == None:
                            callexpr.get_diagnoster().error_panic(
                                ErrorKind.Invalid,
                                f"call: {ident.value} is not a function",
                            )

                        block_reference = IRBlockReference(
                            block_index,
                            self.code.blocks[block_index].signature,
                            ident.diagnoster,
                        )

                        arguments = [
                            self.generate_expr(arg) for arg in callexpr.arguments
                        ]

                        return IRCall(block_reference, arguments)
                    case _:
                        callexpr.get_diagnoster().error_panic(
                            ErrorKind.Invalid,
                            f"call: {callexpr.callable} is not a callable",
                        )
            case _:
                expr.get_diagnoster().error_panic(ErrorKind.Unknown, "expression")
