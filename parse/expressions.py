from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from lex.lexer import Token

if TYPE_CHECKING:
    from .statements import Statement


class ExpressionVisitor:
    def visit_binary(self, expression: Binary):
        pass

    def visit_call(self, expression: Call):
        pass

    def visit_get(self, expression: Get):
        pass

    def visit_grouping(self, expression: Grouping):
        pass

    def visit_literal(self, expression: Literal):
        pass
    
    def visit_logical(self, expression: Logical):
        pass

    def visit_set(self, expression: Set):
        pass

    def visit_super(self, expression: Super):
        pass

    def visit_this(self, expression: This):
        pass

    def visit_unary(self, expression: Unary):
        pass

    def visit_variable(self, expression: Variable):
        pass

    def visit_assignment(self, expression: Assignment):
        pass

    def visit_lambda(self, expression: Lambda):
        pass


@dataclass
class Expression:
    def accept(self, visitor: ExpressionVisitor):
        func = getattr(visitor, f'visit_{self.__class__.__name__.lower()}')
        return func(self)


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Call(Expression):
    callee: Expression
    paren: Token
    arguments: list[Expression]
    

@dataclass
class Get(Expression):
    obj: Expression
    name: Token


@dataclass
class Grouping(Expression):
    expression: Expression


@dataclass
class Literal(Expression):
    value: Any


@dataclass
class Logical(Expression):
    left: Expression
    operator: Token
    right: Expression
    

@dataclass
class Set(Expression):
    obj: Expression
    name: Token
    value: Expression


@dataclass
class Super(Expression):
    keyword: Token
    method: Token

    def __hash__(self):
        return id(self)


@dataclass
class This(Expression):
    keyword: Token

    def __hash__(self):
        return id(self)


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression


@dataclass
class Variable(Expression):
    name: Token

    def __hash__(self):
        return id(self)


@dataclass
class Assignment(Expression):
    name: Token
    value: Expression


@dataclass
class Lambda(Expression):
    params: list[Token]
    body: list[Statement]
