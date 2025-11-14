from typing import Any, Callable

from maxlang.lex import TokenType, Token
from .callable import (
    InternalCallable,
    FunctionCallable,
    Return,
    ClassCallable,
    InstanceCallable,
)
from .expressions import ExpressionVisitor, Expression, Binary, Argument
from .statements import StatementVisitor, Statement
from .environment import Environment, VARIABLE_VALUE_SENTINEL
from maxlang.native_functions import ALL_FUNCTIONS
from maxlang.native_functions.main import BaseInternalInstance
from maxlang.native_functions.BaseTypes.Pair import PairInstance
from maxlang.native_functions.BaseTypes.Bool import BoolInstance
from maxlang.native_functions.BaseTypes.String import StringInstance
from maxlang.native_functions.BaseTypes.VarArgs import VarArgsInstance
from maxlang.errors import InterpreterError, InternalError


class InterpreterBase:
    def __init__(self, interpreter_error: Callable[[InterpreterError], None]):
        self.interpreter_error = interpreter_error
        self.locals: dict[Expression, int] = {}

        self.globals = Environment()
        for name, func in ALL_FUNCTIONS.items():
            self.globals.define(name, func(self))

        self.environment = self.globals

        self.current_call: InternalCallable | None = None

    def execute(self, statement: Statement):
        statement.accept(self)

    def resolve(self, expression: Expression, depth: int):
        self.locals[expression] = depth

    def get_class(self, name: Token):
        return self.environment.get(name)


class ExpressionInterpreter(InterpreterBase, ExpressionVisitor):
    def visit_binary(self, expression):
        match expression.operator.type_:
            case TokenType.GREATER:
                return self.binary_operation(expression, "greaterThan")
            case TokenType.GREATER_EQUAL:
                is_greater = self.binary_operation(expression, "greaterThan").value
                is_equal = self.binary_operation(expression, "equals").value
                return BoolInstance(self).set_value(is_greater or is_equal)
            case TokenType.LESS:
                is_greater = self.binary_operation(expression, "greaterThan").value
                is_equal = self.binary_operation(expression, "equals").value
                return BoolInstance(self).set_value(not is_greater and not is_equal)
            case TokenType.LESS_EQUAL:
                is_greater = self.binary_operation(expression, "greaterThan").value
                return BoolInstance(self).set_value(not is_greater)
            case TokenType.BANG_EQUAL:
                is_equal = self.binary_operation(expression, "equals").value
                return BoolInstance(self).set_value(not is_equal)
            case TokenType.EQUAL_EQUAL:
                return self.binary_operation(expression, "equals")
            case TokenType.PLUS:
                return self.binary_operation(expression, "add")
            case TokenType.MINUS:
                return self.binary_operation(expression, "substract")
            case TokenType.SLASH:
                return self.binary_operation(expression, "divide")
            case TokenType.STAR:
                return self.binary_operation(expression, "multiply")
            case TokenType.INTERPOLATION:
                return self.binary_operation(expression, "add")

        raise ValueError("Max, you forgot to implement something!", expression.operator)

    def binary_operation(self, expression: Binary, method_name: str):
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        try:
            method = left.internal_find_method(method_name)
            value = self.call(expression.operator, method, [right])
            return value
        except (KeyError, AttributeError):
            raise InterpreterError(
                expression.operator,
                f"{left.class_name} does not implement the {method_name} method.",
            )

    def visit_call(self, expression):
        callee = self.evaluate(expression.callee)
        arguments: list[Any] = self.build_arguments(callee, expression.arguments)
        return self.call(expression.paren, callee, arguments)

    def build_arguments(self, callee: InternalCallable, arguments: list[Argument]):
        named_args = (arg for arg in arguments if arg.name is not None)
        arguments_dict = {a.name.lexeme: a for a in named_args}

        args = []
        for argument in arguments:
            if argument.name is not None:
                break

            value = self.evaluate(argument.value)

            # Check if this is an unpack marker
            if (
                isinstance(value, tuple)
                and len(value) == 2
                and value[0] == "__unpack__"
            ):
                # Unpack the values
                args.extend(value[1])
            else:
                args.append(value)

        if callee.parameters and callee.parameters[-1].is_varargs:
            start_index = len(callee.parameters) - 1
            varargs = args[start_index:]
            args = args[:start_index]
            args.append(VarArgsInstance(self).set_values(*varargs))
        else:
            start_index = len(args)

            for parameter in callee.parameters[start_index:]:
                argument = arguments_dict.get(parameter.name.lexeme)
                if (
                    argument is None
                    and parameter.default is None
                    and not parameter.is_varargs
                ):
                    raise InterpreterError(parameter.name, "Argument required in call.")

                if parameter.is_varargs:
                    value = []
                elif argument is not None:
                    value = self.evaluate(argument.value)
                else:
                    value = self.evaluate(parameter.default)
                args.append(value)

        return args

    def call(self, token: Token, function: InternalCallable, arguments: list[Any]):
        if not isinstance(function, InternalCallable):
            raise InterpreterError(token, "Can only call functions and classes.")

        if not function.check_arity(len(arguments)):
            raise InterpreterError(
                token,
                f"Expected between {function.lower_arity()} and {function.upper_arity()} arguments but got {len(arguments)}.",
            )

        previous_call = self.current_call
        self.current_call = function

        try:
            call = function.call(self, arguments)
            self.current_call = previous_call
            return call
        except InternalError as e:
            self.current_call = previous_call
            raise InterpreterError(token, str(e))

    def visit_get(self, expression):
        obj = self.evaluate(expression.obj)
        if isinstance(obj, InstanceCallable):
            return obj.get(expression.name)
        if isinstance(obj, BaseInternalInstance):
            return obj.find_method(expression.name)

        raise InterpreterError(expression.name, "Only instances have properties.")

    def visit_literal(self, expression):
        if expression.type_.klass is None:
            # null literal - return None (used for end of iteration)
            return None
        klass = self.get_class(expression.type_.klass.name)
        try:
            return klass.instance_class(self).set_value(expression.value)
        except InternalError as e:
            self.interpreter_error(InterpreterError(expression.type_.token, str(e)))

    def visit_grouping(self, expression):
        return self.evaluate(expression.expression)

    def visit_logical(self, expression):
        left = self.evaluate(expression.left)
        isTrue = self.unary_operation(expression.operator, expression.left, "toBool")

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
            # set() now returns a new instance
            new_obj = obj.set(expression.name, value)
            return new_obj

        raise InterpreterError(expression.name, "Only instances have fields.")

    def visit_super(self, expression):
        distance = self.locals.get(expression)
        superclasses: ClassCallable = self.environment.get_at(distance, "super")
        obj: InstanceCallable = self.environment.get_at(distance - 1, "self")

        if expression.method:
            method_name = expression.method
        elif isinstance(self.current_call, ClassCallable):
            method_name = Token(
                TokenType.IDENTIFIER, "init", None, expression.keyword.line
            )
        else:
            method_name = (
                self.current_call.name
                if isinstance(self.current_call.name, Token)
                else Token(
                    TokenType.IDENTIFIER,
                    self.current_call.name,
                    None,
                    expression.keyword.line,
                )
            )

        for superclass in superclasses:
            method = superclass.find_method(method_name, check_supers=False)
            if method is not None:
                return method.bind(obj)

        raise InterpreterError(
            method_name,
            f"'{method_name.lexeme}' not found in superclasses of {obj}.",
        )

    def visit_self(self, expression):
        return self.look_up_variable(expression.keyword, expression)

    def visit_unary(self, expression):
        match expression.operator.type_:
            case TokenType.BANG:
                return self.unary_operation(
                    expression.operator, expression.right, "isNotTrue", "toBool"
                )
            case TokenType.MINUS:
                return self.unary_operation(
                    expression.operator, expression.right, "negate"
                )

        return None

    def visit_unpack(self, expression):
        """
        Handle unpacking of iterables using the * operator.
        Returns a special marker that build_arguments will expand.
        """
        iterable = self.evaluate(expression.expression)

        # Check if the object has an iterate method
        try:
            iterate_method = iterable.internal_find_method("iterate")
        except (KeyError, AttributeError):
            raise InterpreterError(
                expression.operator,
                f"{iterable.class_name} is not iterable (no iterate method).",
            )

        # Call iterate to get the iterator
        iterator = self.call(expression.operator, iterate_method, [])

        # Iterate through and collect all values
        values = []
        try:
            next_method = iterator.internal_find_method("next")
        except (KeyError, AttributeError):
            raise InterpreterError(
                expression.operator,
                f"Iterator {iterator.class_name} does not have a next method.",
            )

        while True:
            # next() now returns Pair(value, new_iterator) or None when done
            pair = self.call(expression.operator, next_method, [])

            # Check if we've reached the end (None returned)
            if pair is None:
                break

            # Append the value
            values.append(pair.first)

            # Update iterator for next iteration
            iterator = pair.second
            next_method = iterator.internal_find_method("next")

        # Return a special marker tuple so build_arguments knows to unpack
        return ("__unpack__", values)

    def unary_operation(
        self,
        token: Token,
        obj: Expression,
        method_name: str,
        error_method_name: str | None = None,
    ):
        right = self.evaluate(obj)

        try:
            method = right.internal_find_method(method_name)
            value = self.call(token, method, [])
            return value
        except KeyError:
            raise InterpreterError(
                token,
                f"class {right.class_name} does not implement the {error_method_name or method_name} method.",
            )

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
            self.globals.assign(expression.name.name, value)
        return value

    def visit_lambda(self, expression):
        return FunctionCallable(None, expression, self.environment)

    def visit_pair(self, expression):
        return PairInstance(self).set_values(
            self.evaluate(expression.left), self.evaluate(expression.right)
        )

    def visit_field_update(self, expression):
        from maxlang.native_functions.BaseTypes.String import StringInstance
        from .expressions import Get

        # The left side must be a Get expression (obj.field)
        if not isinstance(expression.obj, Get):
            raise InterpreterError(
                expression.operator,
                "Left side of : must be a field access (e.g., obj.field)",
            )

        # Evaluate the object
        obj = self.evaluate(expression.obj.obj)

        # Get the field name
        field_name = expression.obj.name.lexeme

        # Create a Pair with field name and value
        from maxlang.native_functions.BaseTypes.Pair import PairInstance

        pair = PairInstance(self).set_values(
            StringInstance(self).set_value(field_name), self.evaluate(expression.value)
        )

        # Call copy() on the object
        copy_method = obj.get(Token(TokenType.IDENTIFIER, "copy", None, -1))
        return copy_method.call(self, [pair])

    def visit_if_expression(self, expression):
        isTrue = self.evaluate(expression.condition)

        if not isinstance(isTrue, BoolInstance):
            try:
                isTrue = isTrue.internal_find_method("toBool").call(self, [])
            except KeyError:
                raise InterpreterError(
                    expression.keyword,
                    f"class {isTrue.class_name} does not implement the toBool method.",
                )

        if isTrue.value:
            return self.evaluate(expression.then_branch)
        else:
            return self.evaluate(expression.else_branch)

    def evaluate(self, expression: Expression):
        return expression.accept(self)

    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return

        raise InterpreterError(operator, "Operand must be a number.")

    def stringify(self, obj: Any, keep_string_quotes: bool = False):
        if obj is None:
            return "null"

        if isinstance(obj, StringInstance):
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
        function = FunctionCallable(
            statement.name, statement.function, self.environment
        )
        self.environment.define(statement.name, function)

    def visit_block(self, statement):
        self.execute_block(statement.statements, Environment(self.environment))

    def visit_class(self, statement):
        superclasses: list[Any] = []
        for superclass in statement.superclasses:
            eval_superclass = self.evaluate(superclass)
            superclasses.append(eval_superclass)

        self.environment.define(statement.name)
        self.environment = Environment(self.environment)

        self.environment.define(
            Token(TokenType.IDENTIFIER, "super", None, -1), superclasses
        )

        methods: dict[str, FunctionCallable] = {}
        for method in statement.methods:
            function = FunctionCallable(method.name, method.function, self.environment)
            methods[method.name.lexeme] = function

        klass = ClassCallable(statement.name, superclasses, methods)

        self.environment = self.environment.enclosing
        self.environment.assign(statement.name, klass)

    def visit_variable_statement(self, statement):
        value = VARIABLE_VALUE_SENTINEL
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)

        self.environment.define(statement.name, value)
        return statement.name

    def visit_return_statement(self, statement):
        from .callable import _NO_RETURN_VALUE

        value = _NO_RETURN_VALUE
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
                isTrue = isTrue.internal_find_method("toBool").call(self, [])
            except KeyError:
                raise InterpreterError(
                    statement.keyword,
                    f"class {isTrue.class_name} does not implement the toBool method.",
                )

        if isTrue.value:
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

    def visit_for_statement(self, statement):
        previous = self.environment
        self.environment = Environment(self.environment)

        in_name = self.evaluate(statement.in_name)
        try:
            iterator = in_name.internal_find_method("iterate").call(self, [])
        except InternalError:
            raise InterpreterError(
                statement.keyword,
                "Cannot iterate over instance of that does not implement 'iterate'.",
            )

        while True:
            pair = self.get_next(iterator, statement)

            if pair is None:
                break

            self.environment.define(statement.for_name.name, pair.first)

            self.execute_block(statement.body, self.environment)

            iterator = pair.second

        self.environment = previous

    def get_next(self, iterator, statement):
        try:
            return iterator.internal_find_method("next").call(self, [])
        except InternalError:
            raise InterpreterError(
                statement.keyword,
                f"Iterator {iterator.class_name} that does not implement 'iterate'.",
            )

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
