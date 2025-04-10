from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

from maxlang.lex.lexer import Token

if TYPE_CHECKING:
    from .statements import Statement
    from .callable import FunctionCallable, ClassCallable
    from maxlang.native_functions.main import BaseInternalClass


class ExpressionVisitor:
    def visit_pair(self, expression: Pair):
        pass

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

    def visit_self(self, expression: Self):
        pass

    def visit_unary(self, expression: Unary):
        pass

    def visit_variable(self, expression: Variable):
        pass

    def visit_assignment(self, expression: Assignment):
        pass

    def visit_lambda(self, expression: Lambda):
        pass

    def visit_argument(self, expression: Argument):
        pass

    def visit_if_expression(self, expression: IfExpression):
        pass


@dataclass
class Type:
    klass: FunctionCallable | ClassCallable | type[BaseInternalClass]
    token: Token
    parameters: dict[str, Parameter] = field(default_factory=dict)
    methods: dict[str, Type] = field(default_factory=dict)
    return_type: Type | None = None


@dataclass
class Expression:
    def accept(self, visitor: ExpressionVisitor):
        class_name = "".join(
            "_" + char.lower() if char.isupper() else char
            for char in self.__class__.__name__
        ).lstrip("_")
        func = getattr(visitor, f"visit_{class_name}")
        return func(self)


@dataclass
class Pair(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Call(Expression):
    callee: Variable
    paren: Token
    arguments: list[Argument]


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
    type_: Type


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
    method: Token | None

    def __hash__(self):
        return id(self)


@dataclass
class Self(Expression):
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
    type_: Type | None = None

    def __hash__(self):
        return id(self)


@dataclass
class Assignment(Expression):
    name: Variable
    value: Expression

    def __hash__(self):
        return id(self)


@dataclass
class Parameter:
    type_: Token
    name: Token
    default: Expression | None = None


@dataclass
class Argument(Expression):
    name: Token | None
    value: Expression


@dataclass
class Lambda(Expression):
    token: Token
    params: list[Parameter]
    body: list[Statement]


@dataclass
class IfExpression(Expression):
    condition: Expression
    then_branch: Statement
    else_branch: Statement
    keyword: Token
