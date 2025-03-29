from .statements import StatementVisitor
from .expressions import ExpressionVisitor


class Visitor(StatementVisitor, ExpressionVisitor):
    pass
