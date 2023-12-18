import enum
from dataclasses import dataclass
from .ast import *
from .lexer import Token, TokenKind, sys


class Precedence(enum.Enum):
    Lowest = 0
    Assign = enum.auto()
    Equals = enum.auto()
    LessGreater = enum.auto()
    Sum = enum.auto()
    Product = enum.auto()
    Prefix = enum.auto()
    Call = enum.auto()

    @classmethod
    def from_token(cls, tok: Token):
        match tok.kind:
            case TokenKind.Plus | TokenKind.Minus:
                return cls.Sum
            case TokenKind.Star | TokenKind.ForwardSlash | TokenKind.Percent:
                return cls.Product
            case TokenKind.OpenParen:
                return cls.Call
            case _:
                return cls.Lowest


@dataclass()
class Parser:
    tokens: list[Token]

    def parse(self) -> Program:
        program = Program([])

        while len(self.tokens) > 1 and self.tokens[0] != TokenKind.EOF:
            program.body.append(self.parse_stmt())

        return program

    def parse_stmt(self) -> Statement:
        match self.tokens[0]:
            case tok if tok.kind == TokenKind.Identifier and tok.value == "fn":
                return self.parse_function_definition()
            case tok if tok.kind == TokenKind.Identifier and tok.value == "return":
                return self.parse_return_statement()
            case _:
                return self.parse_expr()

    def parse_function_definition(self) -> FunctionDefinition:
        self.tokens.pop(0)

        if self.tokens[0].kind != TokenKind.Identifier:
            print("expected function name to be identifier", file=sys.stderr)
            exit(1)

        name = Identifier(self.tokens.pop(0).value)

        parameters = self.parse_function_parameters()

        return_type = self.parse_type()

        body = self.parse_function_body()

        return FunctionDefinition(name, parameters, body, return_type)

    def parse_function_parameters(self) -> list[FunctionParameter]:
        parameters = []

        if self.tokens[0].kind != TokenKind.OpenParen:
            print("expected function parameters to start with open paren token", file=sys.stderr)
            exit(1)
        else:
            self.tokens.pop(0)

        while self.tokens[0].kind != TokenKind.CloseParen:
            parameters.append(self.parse_function_parameter())

            if self.tokens[0].kind == TokenKind.Comma:
                self.tokens.pop(0)

                if self.tokens[0].kind != TokenKind.CloseParen:
                    parameters.append(self.parse_function_parameter())

        if self.tokens[0].kind != TokenKind.CloseParen:
            print("expected function parameters to start with open paren token", file=sys.stderr)
            exit(1)
        else:
            self.tokens.pop(0)

        return parameters

    def parse_function_parameter(self) -> FunctionParameter:
        if self.tokens[0].kind != TokenKind.Identifier:
            print("expected an identifier for function parameter name", file=sys.stderr)
            exit(1)

        name = Identifier(self.tokens.pop(0).value)

        expected_type = self.parse_type()

        return FunctionParameter(name, expected_type)

    def parse_function_body(self) -> list[Statement]:
        body = []

        if self.tokens[0].kind != TokenKind.OpenBrace:
            print("expected the start of function body to be open brace", file=sys.stderr)
            exit(1)
        else:
            self.tokens.pop(0)

        while self.tokens[0].kind != TokenKind.CloseBrace:
            body.append(self.parse_stmt())
        self.tokens.pop(0)

        return body

    def parse_return_statement(self) -> ReturnStatement:
        self.tokens.pop(0)

        value = self.parse_expr()

        return ReturnStatement(value)
        

    def parse_type(self) -> Type:
        tok = self.tokens.pop(0)

        match tok.kind:
            case TokenKind.Identifier:
                match tok.value:
                    case "void":
                        return Type.Void
                    case "int":
                        return Type.Integer
                    case "float":
                        return Type.Float
                    case "string":
                        return Type.String
                    case _:
                        print("custom types are not supported yet", file=sys.stderr)
                        exit(1)
            case _:
                print("cannot use this token as a type", file=sys.stderr)
                exit(1)

    def parse_expr(self, precedence: Precedence = Precedence.Lowest) -> Expression:
        lhs = self.parse_unary_expression()

        while (
            len(self.tokens) > 1
            and Precedence.from_token(self.tokens[0]).value > precedence.value
        ):
            lhs = self.parse_binary_expression(lhs)

        return lhs

    def parse_unary_expression(self) -> Expression:
        match self.tokens.pop(0):
            case tok if tok.kind == TokenKind.Identifier:
                return Identifier(tok.value)
            case tok if tok.kind == TokenKind.String:
                return String(tok.value)
            case tok if tok.kind == TokenKind.Integer:
                return Integer(tok.value)
            case tok if tok.kind == TokenKind.Float:
                return Float(tok.value)
            case tok:
                print("invalid expression", file=sys.stderr)
                exit(1)

    def parse_binary_expression(self, lhs: Expression) -> Expression:
        tok = self.tokens.pop(0)

        match tok.kind:
            case TokenKind.Plus | TokenKind.Minus | TokenKind.Star | TokenKind.ForwardSlash | TokenKind.Percent:
                return self.parse_binary_operation(lhs, tok)
            case TokenKind.OpenParen:
                return self.parse_call(lhs)
            case _:
                return lhs

    def parse_binary_operation(self, lhs: Expression, operator: Token) -> BinaryOperation:
        rhs = self.parse_expr(Precedence.from_token(operator))

        return BinaryOperation(lhs, operator, rhs)

    def parse_call(self, lhs: Expression) -> Call:
        arguments = self.parse_call_arguments()

        return Call(lhs, arguments)

    def parse_call_arguments(self) -> list[Expression]:
        arguments = []

        while self.tokens[0].kind != TokenKind.CloseParen:
            arguments.append(self.parse_expr())

            if self.tokens[0].kind == TokenKind.Comma:
                self.tokens.pop(0)

                if self.tokens[0].kind != TokenKind.CloseParen:
                    arguments.append(self.parse_expr())

        if self.tokens[0].kind != TokenKind.CloseParen:
            print("expected call arguments to start with open paren token", file=sys.stderr)
            exit(1)
        else:
            self.tokens.pop(0)

        
        return arguments

