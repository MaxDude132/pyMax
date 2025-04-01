from typing import Any, Callable

from lex import TokenType, Token
from .callable import InternalCallable, FunctionCallable, Return, ClassCallable, InstanceCallable
from .expressions import ExpressionVisitor, Expression, Binary
from .statements import StatementVisitor, Statement
from .environment import Environment, VARIABLE_VALUE_SENTINEL
from native_functions import NATIVE_FUNCTIONS
from native_functions.main import BaseInternalInstance
from native_functions.next import NEXT_SENTINEL
from native_functions.BaseTypes.Pair import PairInstance, PairClass
from native_functions.BaseTypes.Int import IntInstance, IntClass
from native_functions.BaseTypes.Float import FloatInstance, FloatClass
from native_functions.BaseTypes.String import StringInstance, StringClass
from native_functions.BaseTypes.Bool import BoolInstance, BoolClass
from errors import InterpreterError, InternalError


class InterpreterBase:
    def __init__(self, interpreter_error: Callable[[InterpreterError], None]):
        self.interpreter_error = interpreter_error
        self.locals: dict[Expression, int] = {}

        self.globals = Environment()
        for name, func in NATIVE_FUNCTIONS.items():
            token = Token(
                TokenType.IDENTIFIER, name, None, -1
            )
            self.globals.define(token, func(self))

        self.environment = self.globals

        self.current_call: InternalCallable | None = None

    def execute(self, statement: Statement):
        statement.accept(self)

    def resolve(self, expression: Expression, depth: int):
        self.locals[expression] = depth


class ExpressionInterpreter(InterpreterBase, ExpressionVisitor):
    def visit_binary(self, expression):
        match expression.operator.type_:
            case TokenType.GREATER:
                return self.binary_operation(expression, "greaterThan")
            case TokenType.GREATER_EQUAL:
                return self.binary_operation(expression, "greaterThan") or self.binary_operation(expression, "equals")
            case TokenType.LESS:
                return not self.binary_operation(expression, "greaterThan") and not self.binary_operation(expression, "equals")
            case TokenType.LESS_EQUAL:
                return not self.binary_operation(expression, "greaterThan")
            case TokenType.BANG_EQUAL:
                return not self.binary_operation(expression, "equals")
            case TokenType.EQUAL_EQUAL:
                return self.binary_operation(expression, "equals")
            case TokenType.MINUS:
                return self.binary_operation(expression, "substract")
            case TokenType.PLUS:
                return self.binary_operation(expression, "add")
            case TokenType.SLASH:
                return self.binary_operation(expression, "divide")
            case TokenType.STAR:
                return self.binary_operation(expression, "multiply")
            
        return None
    
    def binary_operation(self, expression: Binary, method_name: str):
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        try:
            method = left.internal_find_method(method_name)
            value = self.call(expression.operator, method, [right])
            return value
        except (KeyError, AttributeError):
            raise InterpreterError(expression.operator, f"{left.class_name} does not implement the {method_name} method.")

    
    def visit_call(self, expression):
        callee = self.evaluate(expression.callee)

        arguments: list[Any] = []
        for argument in expression.arguments:
            arguments.append(self.evaluate(argument))

        return self.call(expression.paren, callee, arguments)
        
    def call(self, token: Token, function: InternalCallable, arguments: list[Any]):
        if not isinstance(function, InternalCallable):
            raise InterpreterError(token, "Can only call functions and classes.")
        
        self.current_call = function
        
        if not function.check_arity(len(arguments)):
            raise InterpreterError(token, f"Expected between {function.lower_arity()} and {function.upper_arity()} arguments but got {len(arguments)}.")

        try:
            return function.call(self, arguments)
        except InternalError as e:
            raise InterpreterError(token, str(e))
    
    def visit_get(self, expression):
        obj = self.evaluate(expression.obj)
        if isinstance(obj, InstanceCallable):
            return obj.get(expression.name)
        if isinstance(obj, BaseInternalInstance):
            return obj.find_method(expression.name)

        raise InterpreterError(expression.name, "Only instances have properties.")
    
    def visit_literal(self, expression):
        if isinstance(expression.value, bool):
            klass = self.environment.internal_get(BoolClass.name)
            return BoolInstance(klass, expression.value)
        
        if isinstance(expression.value, int):
            klass = self.environment.internal_get(IntClass.name)
            return IntInstance(klass, expression.value)
        
        if isinstance(expression.value, float):
            klass = self.environment.internal_get(FloatClass.name)
            return FloatInstance(klass, expression.value)
        
        if isinstance(expression.value, str):
            klass = self.environment.internal_get(StringClass.name)
            return StringInstance(klass, expression.value)

        return expression.value
    
    def visit_grouping(self, expression):
        return self.evaluate(expression.expression)
    
    def visit_logical(self, expression):
        left = self.evaluate(expression.left)
        isTrue = self.unary_operation(expression.operator, expression.left, "isTrue")

        if expression.operator.type_ == TokenType.OR:
            if isTrue:
                return left
        else:
            if not isTrue:
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
        obj = self.environment.get_at(distance - 1, "self")

        method = superclass.find_method(expression.method or self.current_call.name, check_supers=False)

        if method is None:
            raise InterpreterError(expression.method, f"Undefined property '{expression.method.lexeme}'.")

        return method.bind(obj)
    
    def visit_self(self, expression):
        return self.look_up_variable(expression.keyword, expression)
    
    def visit_unary(self, expression):
        match expression.operator.type_:
            case TokenType.BANG:
                return self.unary_operation(expression.operator, expression.right, "isNotTrue", "isTrue")
            case TokenType.MINUS:
                return self.unary_operation(expression.operator, expression.right, "negate")
            
        return None
    
    def unary_operation(self, token: Token, obj: Expression, method_name: str, error_method_name: str | None = None):
        right = self.evaluate(obj)

        try:
            method = right.internal_find_method(method_name)
            value = self.call(token, method, [])
            return value
        except KeyError:
            raise InterpreterError(token, f"class {right.class_name} does not implement the {error_method_name or method_name} method.")
    
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
    
    def visit_pair(self, expression):
        klass = self.environment.internal_get(PairClass.name)
        return PairInstance(klass, self.evaluate(expression.left), self.evaluate(expression.right))
    
    def evaluate(self, expression: Expression):
        return expression.accept(self)
    
    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return
        
        raise InterpreterError(operator, "Operand must be a number.")
    
    def stringify(self, obj: Any, keep_string_quotes: bool = False):
        if obj is None:
            return "nil"
        
        if isinstance(obj, str):
            return f'"{obj}"' if keep_string_quotes else obj
        
        if isinstance(obj, InternalCallable):
            try:
                return obj.internal_find_method("toString").call(self, []).value
            except (InternalError, KeyError, AttributeError):
                pass
        
        return str(obj)


class StatementInterpreter(ExpressionInterpreter, StatementVisitor):
    def visit_expression_statement(self, statement):
        self.evaluate(statement.expression)

    def visit_function(self, statement):
        function = FunctionCallable(statement.name, statement.function, self.environment)
        self.environment.define(statement.name, function)

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
            function = FunctionCallable(method.name, method.function, self.environment)
            methods[method.name.lexeme] = function

        klass = ClassCallable(statement.name, superclasses, methods)

        for superclass in statement.superclasses:
            self.environment = self.environment.enclosing

        self.environment.assign(statement.name, klass)

    def visit_variable_statement(self, statement):
        value = VARIABLE_VALUE_SENTINEL
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)

        self.environment.define(statement.name, value)
        return statement.name

    def visit_return_statement(self, statement):
        value = None
        if statement.value is not None:
            value = self.evaluate(statement.value)

        raise Return(value)

    def visit_while_statement(self, statement):
        while self.evaluate(statement.condition):
            self.execute(statement.body)

    def visit_if_statement(self, statement):
        isTrue = self.evaluate(statement.condition)

        if not isinstance(isTrue, BoolInstance):
            try:
                isTrue = isTrue.internal_find_method("isTrue").call(self, [])
            except KeyError:
                raise InterpreterError(statement.keyword, f"class {isTrue.class_name} does not implement the isTrue method.")
        
        if isTrue.value:
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

    def visit_for_statement(self, statement):
        previous = self.environment
        self.environment = Environment(self.environment)
        
        for_name = self.evaluate(statement.for_name)
        in_name = self.evaluate(statement.in_name)
        try:
            node = in_name.internal_find_method("iterate").call(self, [])
        except InternalError:
            raise InterpreterError(statement.keyword, "Cannot iterate over instance of class that does not implement 'iterate'.")

        while node.value is not NEXT_SENTINEL:
            self.environment.assign(for_name, node.value)
            self.execute_block(statement.body, self.environment)
            node = node.next_node

        self.environment = previous

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

