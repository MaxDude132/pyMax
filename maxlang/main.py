import sys

from .lex import Lexer, Token, TokenType
from .parse import Parser, AstPrinter, Interpreter, Resolver, TypeChecker
from .errors import InterpreterError


class Max:
    had_error: bool

    def __init__(self, show_ast=False):
        self.show_ast = show_ast
        self.had_error = False
        self.had_runtime_error = False

    def run_source(self, source: str):
        self.run(source)

    def run_file(self, script: str):
        with open(script) as file:
            source = file.read()

        self.run(source)
        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                line = input("> ")
                self.run(line)
                self.had_error = False
                self.had_runtime_error = False
            except KeyboardInterrupt:
                print("\nExiting Lox REPL")
                break

    def run(self, source: str):
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens, self.parser_error)
        statements = parser.parse()

        for error in lexer.errors:
            self.error(error.line, error.message)

        if self.had_error:
            return

        interpreter = Interpreter(self.interpreter_error)
        resolver = Resolver(interpreter, self.parser_error)
        resolver.resolve_many(statements)

        if self.had_error:
            return
        
        type_checker = TypeChecker(interpreter, self.parser_error)
        type_checker.launch(statements)

        if self.show_ast:
            AstPrinter().print(statements)

        if self.had_error:
            return

        interpreter.interpret(statements)

        if self.had_runtime_error:
            return

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def parser_error(self, token: Token, message: str):
        if token.type_ == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def interpreter_error(self, error: InterpreterError):
        print(f"[line {error.token.line}] {error.message}", file=sys.stderr)
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True
