import platform
import sys
import cli
import compiler.lexer
import compiler.parser
import compiler.ir.gen
import compiler.asm.gen
import compiler.asm.backends.aarch64

from pprint import PrettyPrinter
pprinter = PrettyPrinter()

args = cli.parse_args()

if not args.file_path.is_file() or not args.file_path.exists():
    print(f"{args.file_path}: is not a file", file=sys.stderr)
    exit(1)

with open(args.file_path, "r") as f:
    lexer = compiler.lexer.Lexer(list(f.read()))

tokens = lexer.tokenize()

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

irgen = compiler.ir.gen.IRGen()
ircode = irgen.generate(program)

if args.emit_outputs:
    print("IR :")
    pprinter.pprint(ircode)
    print()

match platform.machine():
    case "aarch64":
        asmbackend = compiler.asm.backends.aarch64.Aarch64Backend()
        asmgen = compiler.asm.gen.ASMGen(asmbackend, ircode)
        asmgen.generate()

        with open(args.file_path.stem + ".s", "w") as f:
            f.write(asmbackend.display_code())

        if args.emit_outputs:
            print("Assembly :")
            print(asmbackend.display_code())
            print()
    case m:
        print(m, "is not a supported machine yet")
        exit(1)
