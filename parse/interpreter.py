from typing import Any, Callable

from lex import TokenType, Token
from .callable import InternalCallable, FunctionCallable, Return, ClassCallable, InstanceCallable
from .expressions import ExpressionVisitor, Expression
from .statements import StatementVisitor, Statement
from .environment import Environment, VARIABLE_VALUE_SENTINEL
from native_functions import NATIVE_FUNCTIONS
from errors import InterpreterError


class InterpreterBase:
    def __init__(self, interpreter_error: Callable[[InterpreterError], None]):
        self.interpreter_error = interpreter_error
        self.locals: dict[Expression, int] = {}

        self.globals = Environment()
        for name, func in NATIVE_FUNCTIONS.items():
            token = Token(
                TokenType.IDENTIFIER, name, None, -1
            )
            self.globals.define(token, func())

        self.environment = self.globals

    def execute(self, statement: Statement):
        statement.accept(self)

    def resolve(self, expression: Expression, depth: int):
        self.locals[expression] = depth


class ExpressionInterpreter(InterpreterBase, ExpressionVisitor):
    def visit_binary(self, expression):
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        match expression.operator.type_:
            case TokenType.GREATER:
                self.check_number_operands(expression.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expression.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.MINUS:
                self.check_number_operands(expression.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                try:
                    return left + right
                except TypeError:
                    raise InterpreterError(expression.operator, "Operands must be two numbers or two strings.")
            case TokenType.SLASH:
                self.check_number_operands(expression.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expression.operator, left, right)
                return float(left) * float(right)
            
        return None
    
    def visit_call(self, expression):
        callee = self.evaluate(expression.callee)

        arguments: list[Any] = []
        for argument in expression.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, InternalCallable):
            print(callee)
            raise InterpreterError(expression.paren, "Can only call functions and classes.")
        
        if len(arguments) != callee.arity():
            raise InterpreterError(expression.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)
    
    def visit_get(self, expression):
        obj = self.evaluate(expression.obj)
        if isinstance(obj, InstanceCallable):
            return obj.get(expression.name)
        
        raise InterpreterError(expression.name, "Only instances have properties.")
    
    def visit_literal(self, expression):
        return expression.value
    
    def visit_grouping(self, expression):
        return self.evaluate(expression.expression)
    
    def visit_logical(self, expression):
        left = self.evaluate(expression.left)

        if expression.operator.type_ == TokenType.OR:
            if left:
                return left
        else:
            if not left:
                return left
            
        return self.evaluate(expression.right)
    
    def visit_set(self, expression):
        obj = self.evaluate(expression.obj)
        if isinstance(obj, InstanceCallable):
            value = self.evaluate(expression.value)
            obj.set(expression.name, value)
            return value
        
        raise InterpreterError(expression.name, "Only instances have fields.")
    
    def visit_super(self, expression):
        distance = self.locals.get(expression)
        superclass: ClassCallable = self.environment.get_at(distance, "super")
        obj = self.environment.get_at(distance - 1, "this")

        method = superclass.find_method(expression.method, check_supers=False)

        if method is None:
            raise InterpreterError(expression.method, f"Undefined property '{expression.method.lexeme}'.")

        return method.bind(obj)
    
    def visit_this(self, expression):
        return self.look_up_variable(expression.keyword, expression)
    
    def visit_unary(self, expression):
        right = self.evaluate(expression.right)

        match expression.operator.type_:
            case TokenType.BANG:
                return not right
            case TokenType.MINUS:
                self.check_number_operand(expression.operator, right)
                return -float(right)
            
        return None
    
    def visit_variable(self, expression):
        return self.look_up_variable(expression.name, expression)
    
    def look_up_variable(self, name: Token, expression: Expression):
        distance = self.locals.get(expression)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)
    
    def visit_assignment(self, expression):
        value = self.evaluate(expression.value)

        distance = self.locals.get(expression)
        if distance is not None:
            self.environment.assign_at(distance, expression.name, value)
        else:
            self.globals.assign(expression.name, value)
        return value
    
    def visit_lambda(self, expression):
        return FunctionCallable(None, expression, self.environment)
    
    def evaluate(self, expression: Expression):
        return expression.accept(self)
    
    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return
        
        raise InterpreterError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return
        
        raise InterpreterError(operator, "Operands must be a number.")
    
    def stringify(self, obj: Any):
        if obj is None:
            return "nil"
        
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]

            return text
        
        return str(obj)


class StatementInterpreter(ExpressionInterpreter, StatementVisitor):
    def visit_expression_statement(self, statement):
        self.evaluate(statement.expression)

    def visit_function(self, statement):
        name = statement.name.lexeme
        function = FunctionCallable(name, statement.function, self.environment)
        self.environment.define(statement.name, function)

    def visit_print(self, statement):
        value = self.evaluate(statement.expression)
        print(self.stringify(value))

    def visit_block(self, statement):
        self.execute_block(statement.statements, Environment(self.environment))

    def visit_class(self, statement):
        superclasses: list[Any] = []
        for superclass in statement.superclasses:
            eval_superclass = self.evaluate(superclass)
            if not isinstance(eval_superclass, ClassCallable):
                raise InterpreterError(superclass.name, "Superclass must be a class.")
            superclasses.append(eval_superclass)

        self.environment.define(statement.name)

        for superclass in superclasses:
            self.environment = Environment(self.environment)
            self.environment.define(
                Token(TokenType.IDENTIFIER, "super", None, -1), superclass
            )

        methods: dict[str, FunctionCallable] = {}
        for method in statement.methods:
            function = FunctionCallable(method.name.lexeme, method.function, self.environment)
            methods[method.name.lexeme] = function

        klass = ClassCallable(statement.name.lexeme, superclasses, methods)

        for superclass in statement.superclasses:
            self.environment = self.environment.enclosing

        self.environment.assign(statement.name, klass)

    def visit_variable_statement(self, statement):
        value = VARIABLE_VALUE_SENTINEL
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)

        self.environment.define(statement.name, value)

    def visit_return_statement(self, statement):
        value = None
        if statement.value is not None:
            value = self.evaluate(statement.value)

        raise Return(value)

    def visit_while_statement(self, statement):
        while self.evaluate(statement.condition):
            self.execute(statement.body)

    def visit_if_statement(self, statement):
        if self.evaluate(statement.condition):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

    def execute_block(self, statements: list[Statement], environment: Environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
        

class Interpreter(StatementInterpreter):
    def interpret(self, statements: list[Statement]):
        try:
            for statement in statements:
                self.execute(statement)
        except InterpreterError as e:
            self.interpreter_error(e)

