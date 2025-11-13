from enum import Enum

from .expressions import ExpressionVisitor, Expression
from .statements import StatementVisitor, Statement, Lambda
from .interpreter import Interpreter
from maxlang.lex import Token


class ClassType(Enum):
    NONE = "None"
    CLASS = "Class"
    SUBCLASS = "Subclass"


class FunctionType(Enum):
    NONE = "None"
    FUNCTION = "Function"
    INITIALIZER = "Initializer"
    METHOD = "Method"


class Resolver(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter: Interpreter, parser_error):
        self.interpreter = interpreter
        self.parser_error = parser_error
        self.scopes: list[dict[str, bool]] = []
        self.current_function: FunctionType = FunctionType.NONE
        self.current_class: ClassType = ClassType.NONE

    def visit_block(self, statement):
        self.begin_scope()
        self.resolve_many(statement.statements)
        self.end_scope()

    def visit_class(self, statement):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(statement.name)
        self.define(statement.name)

        for superclass in statement.superclasses:
            self.current_class = ClassType.SUBCLASS
            if superclass.name.lexeme == statement.name.lexeme:
                self.parser_error(
                    superclass.name, "A class cannot inherit from itself."
                )
        self.resolve_many(statement.superclasses)

        self.begin_scope()
        self.scopes[-1]["super"] = True
        self.begin_scope()
        self.scopes[-1]["self"] = True

        for method in statement.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method.function, declaration)

        self.end_scope()
        self.end_scope()

        self.current_class = enclosing_class

    def resolve_many(self, statements: list[Statement]):
        for statement in statements:
            self.resolve(statement)

    def resolve(self, statement: Statement | Expression):
        statement.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def visit_variable_statement(self, statement):
        self.declare(statement.name)
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        self.define(statement.name)

    def declare(self, name: Token, skip_validation: bool = False):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.parser_error(
                name, f"Already a variable with the name '{name.lexeme}' in this scope."
            )
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        self.scopes[-1][name.lexeme] = True

    def visit_variable(self, expression):
        if self.scopes and self.scopes[-1].get(expression.name.lexeme) is False:
            self.parser_error(
                expression.name, "Can't read local variable in its own initializer."
            )

        self.resolve_local(expression, expression.name)

    def visit_assignment(self, expression):
        self.resolve(expression.value)
        self.resolve_local(expression, expression.name.name)

    def resolve_local(
        self, expression: Expression, name: Token, could_be_global: bool = True
    ):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(
                    expression, len(self.scopes) - (len(self.scopes) - i)
                )

    def visit_function(self, statement):
        self.declare(statement.name)
        self.define(statement.name)

        self.resolve_function(statement.function, FunctionType.FUNCTION)

    def visit_expression_statement(self, statement):
        self.resolve(statement.expression)

    def visit_if_statement(self, statement):
        self.resolve(statement.condition)
        self.resolve(statement.then_branch)
        if statement.else_branch is not None:
            self.resolve(statement.else_branch)

    def visit_return_statement(self, statement):
        if self.current_function == FunctionType.NONE:
            self.parser_error(statement.keyword, "Can't return from top-level code.")

        if statement.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                self.parser_error(
                    statement.keyword, "Cannot return a value from an initialier."
                )

            self.resolve(statement.value)

    def visit_while_statement(self, statement):
        self.resolve(statement.condition)
        self.resolve(statement.body)

    def visit_binary(self, expression):
        self.resolve(expression.left)
        self.resolve(expression.right)

    def visit_call(self, expression):
        self.resolve(expression.callee)
        self.resolve_many(expression.arguments)

    def visit_grouping(self, expression):
        self.resolve(expression.expression)

    def visit_logical(self, expression):
        self.resolve(expression.left)
        self.resolve(expression.right)

    def visit_lambda(self, expression):
        self.resolve_function(expression, FunctionType.FUNCTION)

    def resolve_function(self, function: Lambda, type_: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type_

        self.begin_scope()
        for param in function.params:
            self.declare(param.name)
            self.define(param.name)

        self.resolve_many(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_unary(self, expression):
        self.resolve(expression.right)

    def visit_unpack(self, expression):
        self.resolve(expression.expression)

    def visit_get(self, expression):
        self.resolve(expression.obj)

    def visit_set(self, expression):
        self.resolve(expression.obj)
        self.resolve(expression.value)

    def visit_self(self, expression):
        if self.current_class == ClassType.NONE:
            self.parser_error(
                expression.keyword, "Can't use 'self' outside of a class."
            )

        self.resolve_local(expression, expression.keyword)

    def visit_super(self, expression):
        if self.current_class == ClassType.NONE:
            self.parser_error(
                expression.keyword, "Cannot use 'super' outside of a class."
            )
        elif self.current_class != ClassType.SUBCLASS:
            self.parser_error(
                expression.keyword, "Cannot use 'super' in a class with no superclass."
            )

        self.resolve_local(expression, expression.keyword)

    def visit_for_statement(self, statement):
        self.begin_scope()
        self.resolve(statement.for_name)
        self.resolve(statement.in_name)
        self.resolve_many(statement.body)
        self.end_scope()

    def visit_argument(self, expression):
        self.resolve(expression.value)
