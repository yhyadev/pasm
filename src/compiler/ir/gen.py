import sys
from dataclasses import dataclass, field
from .code import *
from ..ast import *


@dataclass
class IRGen:
    code: IRCode = field(default_factory=IRCode)
    current_block: IRBlock | None = None
    returned: bool = False

    def generate(self, program: Program) -> IRCode:
        for stmt in program.body:
            self.generate_stmt(stmt)

        return self.code

    def generate_stmt(self, stmt: Statement):
        match stmt:
            case funcdef if isinstance(funcdef, FunctionDefinition):
                if self.code.get_block(funcdef.name.value) != None:
                    print(
                        "overloading is not implemented yet", file=sys.stderr
                    )
                    exit(1)

                if self.current_block != None:
                    print(
                        "you can't make a function inside a function", file=sys.stderr
                    )
                    exit(1)

                self.current_block = IRBlock(
                    funcdef.name.value,
                    IRBlockSignature(
                        [parameter.expected_type for parameter in funcdef.parameters],
                        funcdef.return_type,
                    ),
                )

                for stmt in funcdef.body:
                    self.generate_stmt(stmt)

                if not self.returned and self.current_block.signature.return_type != Type.Void:
                    print("expected to return but did not", file=sys.stderr)
                    exit(1)

                self.code.blocks.append(self.current_block)
                self.current_block = None
                self.returned = False
            case returnstmt if isinstance(returnstmt, ReturnStatement):
                if self.current_block == None:
                    print("cannot use return outside a function", file=sys.stderr)
                    exit(1)

                value = self.generate_expr(returnstmt.value)

                if self.current_block.signature.return_type == Type.Void:
                    print("did not expect a return value", file=sys.stderr)
                    exit(1)

                if value.get_type() != self.current_block.signature.return_type:
                    print("types mismatched, return value did not match expected return type", file=sys.stderr)
                    exit(1)

                self.current_block.instructions.append(IRReturn(value))
                self.returned = True
            
            case expr if isinstance(expr, Expression):
                value = self.generate_expr(expr)

                if isinstance(value, IRInstruction):
                    assert self.current_block != None
                    self.current_block.instructions.append(value)
            case _:
                ...

    def generate_expr(self, expr: Expression) -> IRValue:
        if self.current_block == None:
            print("cannot use an expression outside a function", file=sys.stderr)
            exit(1)

        match expr:
            case integerexpr if isinstance(integerexpr, Integer):
                return IRInteger(integerexpr.value)
            case floatexpr if isinstance(floatexpr, Float):
                return IRFloat(floatexpr.value)
            case stringexpr if isinstance(stringexpr, String):
                index = self.code.add_string_literal(IRStringLiteral(stringexpr.value))
                return IRStringReference(index)
            case callexpr if isinstance(callexpr, Call):
                match callexpr.callable:
                    case ident if isinstance(ident, Identifier):
                        block_index = self.code.get_block(ident.value)
                        if block_index == None:
                            print(ident.value, "is not a function", file=sys.stderr)
                            exit(1)

                        blockref = IRBlockReference(block_index, self.code.blocks[block_index].signature)

                        arguments = [self.generate_expr(arg) for arg in callexpr.arguments]

                        return IRCall(blockref, arguments)
                    case _:
                        print(callexpr.callable, "is not a function")
                        exit(1)
            case _:
                print("expression is not implemented yet")
                exit(1)
