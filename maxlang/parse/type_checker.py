from .expressions import ExpressionVisitor, Type, Variable, Super, Parameter
from .statements import StatementVisitor, Statement, Lambda, ReturnStatement
from .interpreter import Interpreter
from .callable import FunctionCallable, ClassCallable
from maxlang.native_functions import NATIVE_FUNCTIONS
from maxlang.native_functions.main import BaseInternalClass
from maxlang.lex import Token, TokenType


class TypeChecker(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter: Interpreter, parser_error):
        self.interpreter = interpreter
        self.parser_error = parser_error
        self.variables: list[dict[str, Type]] = [{}]

        for name, func in NATIVE_FUNCTIONS.items():
            self.variables[-1][name.lexeme] = Type(func(interpreter), Token(TokenType.IDENTIFIER, name, None, -1))

        self.current_function: Token | None = None
        self.current_class: Token | None = None

    def check_many(self, statements: list[Statement]) -> list[Type]:
        ret = []
        for statement in statements:
            ret.append(self.check(statement))
        return ret
                       
    def check(self, statement: Statement) -> Type:
        return statement.accept(self)

    def begin_scope(self):
        self.variables.append({})

    def end_scope(self):
        self.variables.pop()

    def resolve(self, name: Token) -> Type | None:
        for variables in reversed(self.variables):
            if name.lexeme in variables:
                return variables[name.lexeme]
            
        self.parser_error(name, f"Undefined variable '{name.lexeme}'.")

    def validate_type(self, value: Type, expected: Token):
        if value is None:
            return False
        
        if value.klass.name.lexeme == expected.lexeme:
            return True
        
        if hasattr(value.klass, "superclasses"):
            return any(
                superclass.token.lexeme for superclass in value.klass.superclasses
            )
        
        return False
        
    
    def get_common_type(self, old_type: Type, new_type: Type):
        if isinstance(old_type.klass, type) and isinstance(new_type.klass, type) and issubclass(old_type.klass, BaseInternalClass) and issubclass(new_type.klass, BaseInternalClass) and old_type.klass.name == new_type.klass.name:
            return new_type
        if isinstance(old_type.klass, type) and issubclass(old_type.klass, BaseInternalClass) or isinstance(new_type.klass, type) and issubclass(new_type.klass, BaseInternalClass):
            raise TypeError
        
        if isinstance(old_type.klass, FunctionCallable) and isinstance(new_type.klass, FunctionCallable):
            return new_type
        if isinstance(old_type.klass, FunctionCallable) or isinstance(new_type.klass, FunctionCallable):
            raise TypeError
        
        if isinstance(old_type.klass, ClassCallable) and isinstance(new_type.klass, ClassCallable):
            if old_type.klass.name == new_type.klass.name:
                return new_type
        
            for class_name_2 in (new_type.klass.name, *(superclass.token.lexeme for superclass in new_type.klass.superclasses)):
                for class_name_1 in (old_type.klass.name, *(superclass.token.lexeme for superclass in old_type.klass.superclasses)):
                    if class_name_2 == class_name_1:
                        return self.variables[-1][class_name_2]
                    
        raise TypeError

    def get_type(self, name: Token, raise_error=True) -> Type:
        for variable_scope in reversed(self.variables):
            if name.lexeme in variable_scope:
                return variable_scope[name.lexeme]
        
        if raise_error:
            self.parser_error(name, f"Undefined variable '{name.lexeme}'.")

    def visit_function(self, statement):
        type_ = self.type_check_function(statement.function)
        self.variables[-1][statement.name.lexeme] = type_
        return type_

    def visit_lambda(self, expression):
        return self.type_check_function(expression)

    def type_check_function(self, statement: Lambda) -> Type:
        previous_function = self.current_function
        self.current_function = statement.token

        self.begin_scope()
        self.set_parameters(statement.params)
        ret_indexes = self.get_return_indexes(statement.body)
        body_types = self.check_many(statement.body)
        try:
            ret_type = self.get_return_type(ret_indexes, body_types)
            if ret_type is None and self.current_class is not None:
                # -1 is function scope, -2 is class scope, -3 is outside scope where class is defined
                ret_type = self.variables[-3].get(self.current_class.lexeme)
        except TypeError:
            self.parser_error(statement.token, "Multiple return types found for function.")
        self.end_scope()

        self.current_function = previous_function

        return Type(
            FunctionCallable(statement.token, Lambda(statement.token, statement.params, statement.body), self.interpreter.environment),
            statement.token,
            {p.name.lexeme: p for p in statement.params},
            return_type=ret_type,
        )
    
    def set_parameters(self, parameters: list[Parameter]):
        for parameter in parameters:
            type_ = self.resolve(parameter.type_)
            self.variables[-1][parameter.name.lexeme] = type_
    
    def get_return_indexes(self, body: list[Statement]) -> list[int]:
        return [i for i, s in enumerate(body) if isinstance(s, ReturnStatement)]

    def get_return_type(self, ret_indexes: list[int], body_types: list[Type | None]) -> Type | None:
        ret = None

        for ret_index in ret_indexes:
            ret_type = body_types[ret_index]
            if ret is not None:
                ret = self.get_common_type(ret, ret_type)
            else:
                ret = ret_type

        return ret

    def visit_expression_statement(self, statement):
        return self.check(statement.expression)

    def visit_call(self, expression):
        callee_type = self.check(expression.callee)
        if callee_type is None:
            try:
                callee_type = self.get_type(expression.callee.name, False)
                expression.callee.type_ = callee_type
            except AttributeError:
                pass

        if callee_type is None:  # Means the function does not exist. The interpreter gives an error for it already.
            return 

        argument_values = [self.check(arg.value) for arg in expression.arguments]
        if len(callee_type.parameters) != len(argument_values):
            return callee_type.return_type   # TODO: Raise an error. For now, we don't validate internal functions and classes, so we need to pass here
        
        for arg_structure, arg, (param_name, param) in zip(expression.arguments, argument_values, callee_type.parameters.items(), strict=True):
            if not self.validate_type(arg, param.type_):
                arg_name = arg_structure.value.name if isinstance(arg_structure.value, Variable) else arg.token
                got_arg_name = arg.klass.name.lexeme if arg is not None else None
                callee_name = expression.callee.keyword.lexeme if isinstance(expression.callee, Super) else expression.callee.name.lexeme
                self.parser_error(arg_name, f"Expected {param.type_.lexeme} but got {got_arg_name} for parameter {param_name} in call to {callee_name}.")

        return callee_type.return_type

    def visit_variable(self, expression):
        if expression.type_ is not None:
            return expression.type_
        
        if expression.name.lexeme in self.variables[-1]:
            return self.variables[-1][expression.name.lexeme]
        
        return self.get_type(expression.name, raise_error=False)
        
    
    def visit_literal(self, expression):
        return expression.type_
    
    def visit_assignment(self, expression):
        previous_type = self.variables[-1].get(expression.name.name.lexeme)
        new_type = self.check(expression.value)

        if previous_type is not None:
            try:
                expression.name.type_ = self.get_common_type(previous_type, new_type)
            except TypeError:
                previous_type_name = previous_type.klass.name.lexeme
                new_type_name = new_type.klass.name.lexeme
                self.parser_error(expression.name.name, f"Cannot redefine variable of type {previous_type_name} to type {new_type_name}.")
        else:
            expression.name.type_ = new_type

        self.variables[-1][expression.name.name.lexeme] = expression.name.type_
        return expression.name.type_
    
    def visit_block(self, statement):
        self.begin_scope()
        self.check_many(statement.statements)
        self.end_scope()

    def visit_class(self, statement):
        previous_class = self.current_class
        self.current_class = statement.name

        superclasses = [
            self.variables[-1].get(s.name.lexeme) for s in statement.superclasses
        ]
        klass = ClassCallable(statement.name, superclasses, {})
        type_ = Type(klass, statement.name)
        self.variables[-1][statement.name.lexeme] = type_

        self.begin_scope()
        self.variables[-1]["self"] = type_
        method_types = self.check_many(statement.methods)
        self.end_scope()

        self.current_class = previous_class

        method_types_dict = {m.token.lexeme: m for m in method_types}
        methods = {
            m.token.lexeme: m.parameters for m in method_types
        }
        klass.methods = methods
        type_.parameters = methods.get("init", {})
        type_.methods = method_types_dict
        type_.return_type = type_

        return type_
    
    def visit_super(self, expression):
        if self.current_class is None:
            return
        if self.current_function is None:
            return

        class_type = self.resolve(self.current_class)
        function_name = expression.method.lexeme if expression.method is not None else self.current_function.lexeme

        for superclass in class_type.klass.superclasses:
            function = superclass.methods.get(function_name)
            if function is not None:
                return function

    def visit_set(self, expression):
        obj = self.check(expression.obj)
        previous_type = self.variables[-1].get(expression.name.lexeme)
        new_type = self.check(expression.value)

        if previous_type is None:
            obj.methods[expression.name.lexeme] = new_type
            return new_type
        
        try:
            type_ = self.get_common_type(previous_type, new_type)
        except TypeError:
            previous_type_name = previous_type.klass.name.lexeme
            new_type_name = new_type.klass.name.lexeme
            self.parser_error(expression.name, f"Cannot redefine attribute of type {previous_type_name} to type {new_type_name}.")
        else:
            return type_

    
    def visit_self(self, expression):
        return self.resolve(expression.keyword)
    
    def visit_return_statement(self, statement):
        return self.check(statement.value)
    
    def visit_if_expression(self, expression):
        then_type = self.check(expression.then_branch)
        else_type = self.check(expression.else_branch)

        try:
            return self.get_common_type(then_type, else_type)
        except TypeError:
            previous_type_name = then_type.klass.name.lexeme
            new_type_name = else_type.klass.name.lexeme
            self.parser_error(expression.keyword, f"Got different return types in if expression: {previous_type_name} and {new_type_name}.")

