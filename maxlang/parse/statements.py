from __future__ import annotations
from dataclasses import dataclass

from maxlang.lex.lexer import Token
from .expressions import Expression, Lambda, Variable


class StatementVisitor:
    def visit_expression_statement(self, statement: ExpressionStatement):
        pass

    def visit_function(self, statement: Function):
        pass

    def visit_variable_statement(self, statement: VariableStatement):
        pass

    def visit_block(self, statement: Block):
        pass

    def visit_class(self, statement: Class):
        pass

    def visit_if_statement(self, statement: IfStatement):
        pass

    def visit_return_statement(self, statement: ReturnStatement):
        pass

    def visit_while_statement(self, statement: WhileStatement):
        pass

    def visit_for_statement(self, statement: ForStatement):
        pass


@dataclass
class Statement:
    def accept(self, visitor: StatementVisitor):
        class_name = ''.join(
            '_' + char.lower() if char.isupper() else char
            for char in self.__class__.__name__
        ).lstrip('_')
        func = getattr(visitor, f'visit_{class_name}')
        return func(self)


@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class Function(Statement):
    name: Token
    function: Lambda


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Statement
    keyword: Token


@dataclass
class VariableStatement(Statement):
    name: Token
    initializer: Expression


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class Class(Statement):
    name: Token
    superclasses: list[Variable]
    methods: list[Function]


@dataclass
class ReturnStatement(Statement):
    keyword: Token
    value: Expression


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Statement


@dataclass
class ForStatement(Statement):
    keyword: Token
    for_name: Variable
    in_name: Variable
    body: list[Statement]
