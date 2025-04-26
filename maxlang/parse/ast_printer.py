from .expressions import Expression
from .statements import Statement
from .visitor import Visitor
from maxlang.native_functions.BaseTypes.Pair import PairClass


class AstPrinter(Visitor):
    def print(self, statements: list[Statement]) -> str:
        for statement in statements:
            print(statement.accept(self))

    def visit_binary(self, expression) -> str:
        return self.parenthesize(
            expression.operator.lexeme, expression.left, expression.right
        )

    def visit_grouping(self, expression) -> str:
        return self.parenthesize("group", expression.expression)

    def visit_literal(self, expression) -> str:
        if expression.value is None:
            return "null"
        if isinstance(expression.value, str):
            return f'"{expression.value}"'

        return str(expression.value)

    def visit_logical(self, expression):
        return self.parenthesize(
            expression.operator.lexeme, expression.left, expression.right
        )

    def visit_unary(self, expression) -> str:
        return self.parenthesize(expression.operator.lexeme, expression.right)

    def visit_variable(self, expression):
        return self.parenthesize(f"getvar {expression.name.lexeme}")

    def visit_assignment(self, expression):
        return self.parenthesize(f"setvar {expression.name.name.lexeme}", expression.value)

    def visit_expression_statement(self, statement):
        return statement.expression.accept(self)

    def visit_block(self, statement):
        string = self.parenthesize("block") + "\n"

        for stmt in statement.statements:
            string += stmt.accept(self) + "\n"

        string += self.parenthesize("endblock")
        return string

    def visit_class(self, statement):
        string = self.parenthesize(f"class {statement.name.lexeme}") + "\n"

        for method in statement.methods:
            string += self.visit_function(method, "method") + "\n"

        string += self.parenthesize(f"endclass {statement.name.lexeme}")
        return string

    def visit_variable_statement(self, statement):
        return self.parenthesize(f"var {statement.name.lexeme}", statement.initializer)

    def visit_if_statement(self, statement):
        string = self.parenthesize("if", statement.condition)
        string += "\n" + self.parenthesize("then", statement.then_branch)

        if statement.else_branch is not None:
            string += "\n" + self.parenthesize("else", statement.else_branch)

        return string

    def visit_if_expression(self, expression):
        string = self.parenthesize("if", expression.condition)
        string += "\n" + self.parenthesize("then", expression.then_branch)
        string += "\n" + self.parenthesize("else", expression.else_branch)

        return string

    def visit_while_statement(self, statement):
        return self.parenthesize("while", statement.condition, statement.body)

    def visit_call(self, expression):
        return self.parenthesize("call", expression.callee, *expression.arguments)

    def visit_function(self, statement, function_type="function"):
        string = (
            self.parenthesize(
                f"{function_type} {statement.name.lexeme}({', '.join(f"{'varargs ' if s.is_varargs else ''}{s.types[0].lexeme} {s.name.lexeme}" for s in statement.function.params)})"
            )
            + "\n"
        )

        for s in statement.function.body:
            string += s.accept(self) + "\n"

        string += self.parenthesize(f"end{function_type}")

        return string

    def visit_lambda(self, expression):
        string = (
            self.parenthesize(
                f"lambda({', '.join(s.lexeme for s in expression.params)})"
            )
            + "\n"
        )

        for s in expression.body:
            string += s.accept(self) + "\n"

        string += self.parenthesize("endlambda")

        return string

    def visit_return_statement(self, statement):
        return self.parenthesize("return", statement.value)

    def visit_get(self, expression):
        return self.parenthesize(f"get {expression.name.lexeme}", expression.obj)

    def visit_set(self, expression):
        return self.parenthesize(
            f"set {expression.name.lexeme}", expression.value, expression.obj
        )

    def visit_self(self, expression):
        return self.parenthesize(f"var {expression.keyword.lexeme}")

    def visit_super(self, expression):
        return self.parenthesize(
            f"super {expression.method.lexeme if expression.method else ''}"
        )

    def visit_pair(self, expression):
        return self.parenthesize(PairClass.name, expression.left, expression.right)

    def visit_for_statement(self, statement):
        string = self.parenthesize("for", statement.for_name, statement.in_name)

        for s in statement.body:
            string += "\n" + self.parenthesize("do", s)

        string += self.parenthesize("endfor")
        return string

    def visit_argument(self, expression):
        if expression.name is None:
            return expression.value.accept(self)
        
        return f"{expression.name.lexeme}:{expression.value.accept(self)}"

    def parenthesize(self, name: str, *expressions: Expression) -> str:
        string = f"({name}"

        for expression in expressions:
            if expression is not None:
                string += " "
                string += expression.accept(self)

        string += ")"
        return string
