import platform
import sys
import cli
from compiler.errors import Diagnoster
import compiler.preprocessor
import compiler.lexer
import compiler.parser
import compiler.ir.gen
import compiler.asm.gen
import compiler.asm.backends.aarch64

from pprint import PrettyPrinter

pprinter = PrettyPrinter()

args = cli.parse_args()

if not args.file_path.is_file():
    print(f"{args.file_path} is not a file", file=sys.stderr)
    exit(1)

with open(args.file_path, "r") as f:
    lexer = compiler.lexer.Lexer(list(f.read()), Diagnoster(args.file_path))

tokens = lexer.tokenize()
tokens = compiler.preprocessor.Preprocessor(
    tokens, [args.file_path]
).preprocess_tokens()

if args.emit_outputs:
    print("Tokens :")
    pprinter.pprint(tokens)
    print()

parser = compiler.parser.Parser(tokens)
program = parser.parse()

if args.emit_outputs:
    print("AST :")
    pprinter.pprint(program)
    print()

ir_gen = compiler.ir.gen.IRGen(program)
ir_gen.generate()

if args.emit_outputs:
    print("IR :")
    pprinter.pprint(ir_gen.code)
    print()

match platform.machine():
    case "aarch64":
        asm_backend = compiler.asm.backends.aarch64.Aarch64Backend()
        asm_gen = compiler.asm.gen.ASMGen(asm_backend, ir_gen.code)
        asm_gen.generate()

        if args.emit_outputs:
            print("Assembly :")
            print(asm_backend.display_code())

        with open(args.file_path.stem + ".s", "w") as f:
            f.write(asm_backend.display_code())
    case m:
        print(m, "is not a supported machine yet")
        exit(1)
