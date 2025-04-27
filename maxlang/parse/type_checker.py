from .expressions import ExpressionVisitor, Type, Variable, Super, Parameter, Literal, Binary, Call, Pair, Grouping, Unary, Get, Argument
from .statements import StatementVisitor, Statement, Lambda
from .interpreter import Interpreter
from .callable import FunctionCallable, ClassCallable, InternalCallable
from maxlang.native_functions import BUILTIN_TYPES, INTERNAL_TYPES, ALL_FUNCTIONS
from maxlang.native_functions.main import BaseInternalClass, make_internal_token
from maxlang.lex import Token, TokenType
from maxlang.errors import InternalError
from maxlang.native_functions.BaseTypes.Object import ObjectClass
from maxlang.native_functions.BaseTypes.Pair import PairClass


class TypeCheckerError(Exception):
    pass


class Deferred:
    def __init__(self, name: Token):
        self.name = name


class TypeChecker(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter: Interpreter, parser_error):
        self.interpreter = interpreter

        def internal_parser_error(token: Token, message: str):
            parser_error(token, message)
            raise TypeCheckerError

        self.parser_error = internal_parser_error
        self.variables: list[dict[str, Type]] = [{}]

        all_builtin = {**BUILTIN_TYPES, **INTERNAL_TYPES}

        for name, func in all_builtin.items():
            function = func(interpreter)
            self.variables[-1][name.lexeme] = Type(function, make_internal_token(name.lexeme), parameters=function.parameters)
            self.variables[-1][name.lexeme].return_type = self.variables[-1][name.lexeme]

        for name, func in ALL_FUNCTIONS.items():
            if name.lexeme not in self.variables[-1]:
                function = func(interpreter)
                return_type = self.variables[-1].get(function.return_token.lexeme)
                self.variables[-1][name.lexeme] = Type(func(interpreter), make_internal_token(name.lexeme), parameters=function.parameters, return_type=return_type)

            function = self.variables[-1][name.lexeme].klass
            methods = getattr(function, "methods", {})
            if not methods:
                continue

            method_types = {}
            instance = function.instance_class(interpreter)
            for method_name, method_class in methods.items():
                method = method_class(instance)
                type_ = self.variables[-1].get(method.return_token.lexeme)
                method_types[method_name] = Type(method, make_internal_token(method_name), parameters=method.parameters, return_type=type_)
            self.variables[-1][name.lexeme].methods = method_types

        for name in INTERNAL_TYPES:
            # These types are reserved to internal functionalities
            self.variables[-1].pop(name.lexeme)

        self.current_function: Token | None = None
        self.current_function_return_types = []
        self.current_class: Token | None = None
        self.current_method_calls_super = False

    def launch(self, statements: list[Statement]):
        try:
            self.check_many(statements)
        except TypeCheckerError:
            pass

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

        if expected.lexeme == ObjectClass.name.lexeme:
            return True
        
        if value.klass.name.lexeme == expected.lexeme:
            return True
        
        if hasattr(value, "superclasses"):
            return any(
                superclass.token.lexeme == expected.lexeme for superclass in value.superclasses
            )
        
        return False
        
    
    def get_common_type(self, old_type: Type | Deferred, new_type: Type | Deferred):
        if isinstance(old_type, Deferred):
            return new_type
        
        if isinstance(new_type, Deferred):
            return old_type

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
        
            for class_name_2 in (new_type.klass.name, *(superclass.token.lexeme for superclass in new_type.superclasses)):
                for class_name_1 in (old_type.klass.name, *(superclass.token.lexeme for superclass in old_type.superclasses)):
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
        self.current_method_calls_super = False
        previous_function = self.current_function
        self.current_function = statement.token
        previous_return_types = self.current_function_return_types
        self.current_function_return_types = []

        self.begin_scope()
        self.set_parameters(statement.params)
        self.check_many(statement.body)
        try:
            ret_type = self.get_return_type()
            if ret_type is None and self.current_class is not None:
                # -1 is function scope, -2 is class scope, -3 is outside scope where class is defined
                ret_type = self.variables[-3].get(self.current_class.lexeme)
        except TypeError:
            self.parser_error(statement.token, "Multiple return types found for function.")
        self.end_scope()

        self.current_function = previous_function
        self.current_function_return_types = previous_return_types

        return Type(
            FunctionCallable(statement.token, Lambda(statement.token, statement.params, statement.body), self.interpreter.environment),
            statement.token,
            statement.params,
            return_type=ret_type,
            calls_super=self.current_method_calls_super
        )
    
    def set_parameters(self, parameters: list[Parameter]):
        for parameter in parameters:
            type_ = self.resolve(parameter.types[0])
            self.variables[-1][parameter.name.lexeme] = type_

    def get_return_type(self) -> Type | None:
        ret = None

        for type_ in self.current_function_return_types:
            if ret is not None:
                ret = self.get_common_type(ret, type_)
            else:
                ret = type_

        return ret

    def visit_expression_statement(self, statement):
        return self.check(statement.expression)

    def visit_call(self, expression):
        if (
            self.current_function is not None 
            and hasattr(expression.callee, "name") 
            and (
                self.current_class is None
                or not isinstance(expression.callee, Variable)
                and isinstance(expression.callee.obj, Get)
                and expression.callee.obj.name == 'self'
            ) and expression.callee.name.lexeme == self.current_function.lexeme
        ):
            # Note: If the call has recursion, the return type will not be known until
            #   the rest of the function has been parsed. In this case, we defer the type 
            #   to be evaluated once the return type has been set. 
            return Deferred(expression.callee.name)

        callee_type = self.check(expression.callee)
        if callee_type is None:
            try:
                callee_type = self.get_type(expression.callee.name, False)
                expression.callee.type_ = callee_type
            except AttributeError:
                pass

        if callee_type is None:
            self.parser_error(expression.callee.name, f"Function {expression.callee.name.lexeme} not found.")
            return 
        
        try:
            parameters = self.get_parameters(callee_type.klass, expression.arguments, callee_type.parameters)
        except InternalError as e:
            self.parser_error(expression.callee.name, str(e).format(expression.callee.name.lexeme))

        callee_name = expression.callee.keyword if isinstance(expression.callee, Super) else expression.callee.name
        self.validate_parameters(expression.arguments, parameters, callee_name)

        return callee_type.return_type
    
    def get_arg_name(self, arg_structure_value):
        if isinstance(arg_structure_value, Variable):
            return arg_structure_value.name
        if isinstance(arg_structure_value, Literal):
            return arg_structure_value.type_.token
        if isinstance(arg_structure_value, Binary):
            return self.get_arg_name(arg_structure_value.right)
        if isinstance(arg_structure_value, Call):
            return arg_structure_value.callee.name
        if isinstance(arg_structure_value, Pair):
            return arg_structure_value.operator
        if isinstance(arg_structure_value, Grouping):
            return self.get_arg_name(arg_structure_value.expression)
        if isinstance(arg_structure_value, Unary):
            return arg_structure_value.operator
        if isinstance(arg_structure_value, Get):
            return arg_structure_value.name
        if isinstance(arg_structure_value, Argument):
            return self.get_arg_name(arg_structure_value.value)
        return arg_structure_value.token
    
    def get_parameters(self, klass: InternalCallable, arguments: list[Type], parameters: list[Parameter]) -> list[Parameter]:
        parameters = parameters.copy()
        lower_arity, upper_arity = self.get_arity(klass)
        arguments_length = len(arguments)

        if lower_arity > arguments_length or upper_arity < arguments_length:
            raise InternalError(f"Expected between {lower_arity} and {upper_arity} arguments in call to {{}} but got {arguments_length}.")
        
        if not parameters:
            return []
        
        if parameters[-1].is_varargs:
            # VarArgs is not added until we're certain it is required, since it could be empty
            vararg = parameters[-1]
            parameters = parameters[:-1]
            for _ in range(arguments_length - (len(parameters))):
                parameters.append(vararg)

        return parameters
    
    def get_arity(self, klass: InternalCallable) -> tuple[int, int]:
        minimum = klass.lower_arity()
        maximum = klass.upper_arity()

        return minimum, maximum
    
    def validate_parameters(self, all_arguments: list[Argument], parameters: list[Parameter], callee_name: Token):
        arguments = [arg for arg in all_arguments if arg.name is None]
        argument_names = [self.get_arg_name(arg) for arg in arguments]
        argument_types = self.check_many(arguments)
        named_arguments = {arg.name.lexeme: arg for arg in all_arguments if arg.name is not None}

        if len(arguments) < len(parameters):
            for parameter in parameters[len(arguments):]:
                if parameter.name.lexeme in named_arguments:
                    name = self.get_arg_name(named_arguments[parameter.name.lexeme])
                    type_ = self.check(named_arguments[parameter.name.lexeme])
                else:
                    name = parameter.name
                    type_ = self.resolve(parameter.types[0])
                
                argument_names.append(name)
                argument_types.append(type_)

        for arg_name, arg_type, param in zip(argument_names, argument_types, parameters, strict=True):
            if not self.validate_type(arg_type, param.types[0]):
                got_arg_name = arg_type.klass.name.lexeme if arg_type is not None else None
                self.parser_error(arg_name, f"Expected {param.types[0].lexeme} but got {got_arg_name} for parameter {param.name.lexeme} in call to {callee_name.lexeme}.")


    def visit_variable(self, expression):
        if expression.type_ is not None:
            return expression.type_
        
        if expression.name.lexeme in self.variables[-1]:
            return self.variables[-1][expression.name.lexeme]
        
        return self.get_type(expression.name, raise_error=True)
        
    
    def visit_literal(self, expression):
        return self.resolve(expression.type_.klass.name)
    
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
        klass = ClassCallable(statement.name, [s.klass for s in superclasses], {})
        type_ = Type(klass, statement.name, superclasses=superclasses)
        self.variables[-1][statement.name.lexeme] = type_

        self.begin_scope()
        self.variables[-1]["self"] = type_
        type_.methods["self"] = type_

        method_types = self.check_many(statement.methods)
        method_types_dict = {m.token.lexeme: m for m in method_types}
        methods = {
            m.token.lexeme: m.klass for m in method_types
        }
        klass.methods.update(methods)
        init = method_types_dict.get("init") or self.get_method_from_super(type_, make_internal_token("init"))
        type_.parameters = init.parameters if init is not None else {}
        type_.methods.update(method_types_dict)
        type_.methods["init"] = init
        type_.return_type = type_

        self.end_scope()
        self.current_class = previous_class

        return type_
    
    def visit_super(self, expression):
        if self.current_class is None:
            return
        if self.current_function is None:
            return

        self.current_method_calls_super = True
        class_type = self.resolve(self.current_class)
        function_name = expression.method.lexeme

        for superclass in class_type.superclasses:
            function = superclass.methods.get(function_name)
            if function is not None:
                return function

    def visit_set(self, expression):
        obj = self.check(expression.obj)
        previous_type = obj.methods.get(expression.name.lexeme)
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
            obj.methods[expression.name.lexeme] = type_
            return type_
        
    def visit_get(self, expression):
        obj = self.check(expression.obj)
        ret = obj.methods.get(expression.name.lexeme)

        if ret is None:
            return self.get_method_from_super(obj, expression.name)

        if ret is None:
            self.parser_error(expression.name, f"Attribute {expression.name.lexeme} not found for class {obj.klass.name.lexeme}.")

        return ret
    
    def get_method_from_super(self, type_: Type, name: Token):
        for superclass in type_.superclasses:
            if name.lexeme in superclass.methods:
                ret = superclass.methods[name.lexeme]
                if ret is None and (method := superclass.methods[name.lexeme]) and method.calls_super:
                    return self.get_method_from_super(superclass, name)
                return ret
            if (
                "self" in superclass.methods
                and name.lexeme in superclass.methods["self"].methods
            ):
                return superclass.methods["self"].methods.get(name.lexeme)
            
            if (init := superclass.methods.get("init")) and init.calls_super:
                return self.get_method_from_super(superclass, name)
            
    
    def visit_self(self, expression):
        return self.resolve(expression.keyword)
    
    def visit_return_statement(self, statement):
        ret = self.check(statement.value)
        self.current_function_return_types.append(ret)
        return ret
    
    def visit_if_expression(self, expression):
        then_type = self.check(expression.then_branch)
        else_type = self.check(expression.else_branch)

        try:
            return self.get_common_type(then_type, else_type)
        except TypeError:
            previous_type_name = then_type.klass.name.lexeme
            new_type_name = else_type.klass.name.lexeme
            self.parser_error(expression.keyword, f"Got different return types in if expression: {previous_type_name} and {new_type_name}.")

    def visit_argument(self, expression):
        return self.check(expression.value)
    
    def visit_unary(self, expression):
        if expression.operator.type_ == TokenType.BANG:
            return self.variables[0]["Bool"]
        
        right_type = self.check(expression.right)

        try:
            return right_type.methods["negate"].return_type
        except KeyError:
            self.parser_error(expression.operator, f"{right_type.token.lexeme} does not implement the negate method.")
    
    def visit_grouping(self, expression):
        return self.check(expression.expression)
    
    def visit_variable_statement(self, statement):
        return super().visit_variable_statement(statement)
    
    def visit_pair(self, expression):
        return self.resolve(PairClass.name)
    
    def visit_binary(self, expression):
        left_type = self.check(expression.left)

        match expression.operator.type_:
            case TokenType.PLUS:
                method = "add"
            case TokenType.MINUS:
                method = "substract"
            case TokenType.STAR:
                method = "multiply"
            case TokenType.SLASH:
                method = "divide"
            case TokenType.EQUAL_EQUAL:
                method = "equals"
            case TokenType.BANG_EQUAL:
                # We do not need to call the right function, we just need the return
                #   type. Not equals simply inverts the result of equals, so this is fine.
                method = "equals"
            case TokenType.GREATER:
                method = "greaterThan"
            case TokenType.GREATER_EQUAL:
                method = "greaterThan"
            case TokenType.LESS:
                method = "greaterThan"
            case TokenType.LESS_EQUAL:
                method = "greaterThan"
            case TokenType.INTERPOLATION:
                method = "add"
            case _:
                raise ValueError("Max, you forgot to implement something!", expression.operator)

        obj = left_type.methods.get(method)
        if obj is None:
            self.parser_error(expression.operator, f"<{left_type.klass.name.lexeme}> does not implement the {method} method.")

        argument = Argument(None, expression.right)
        self.validate_parameters([argument], obj.parameters, obj.klass.name)

        return obj.return_type
    
    def visit_for_statement(self, statement):
        in_name = self.check(statement.in_name)
        self.begin_scope()
        iterate = in_name.methods.get("iterate")

        if iterate is None:
            self.parser_error(statement.keyword, f"Cannot iterate over instance of {in_name.klass.class_name} that does not implement 'iterate'.")

        next_ = iterate.return_type.methods.get("next")

        if next_ is None:
            self.parser_error(statement.keyword, f"Cannot get next value from iterator {iterate.class_name} that does not implement 'next'.")

        self.variables[-1][statement.for_name.name.lexeme] = next_.return_type
        self.check_many(statement.body)
        self.end_scope()
    
    def visit_if_statement(self, statement):
        self.check(statement.then_branch)

        if statement.else_branch is not None:
            self.check(statement.else_branch)
    
    def visit_logical(self, expression):
        return super().visit_logical(expression)
    
    def visit_while_statement(self, statement):
        return super().visit_while_statement(statement)

