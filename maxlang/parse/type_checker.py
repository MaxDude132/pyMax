from .expressions import (
    ExpressionVisitor,
    Type,
    Variable,
    Super,
    Parameter,
    Literal,
    Binary,
    Call,
    Pair,
    Grouping,
    Unary,
    Get,
    Argument,
    Unpack,
)
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


class ReturnPath:
    """Represents one possible return path in a function.

    Can be:
    - A concrete type (e.g., return 2, return "hello")
    - A parameter (e.g., return arg_1)
    - A method chain on a parameter (e.g., return arg_1.toString() or return arg_1.add(1).toString())
    """

    def __init__(
        self,
        parameter_name: str | None = None,
        method_chain: list[str] = None,
        concrete_type: Type | None = None,
    ):
        self.parameter_name = parameter_name  # Name of the parameter if this return depends on a parameter
        self.method_chain = (
            method_chain or []
        )  # List of method names called in sequence
        self.concrete_type = concrete_type  # If this is a concrete return value

    def is_parameter_dependent(self) -> bool:
        """Returns True if this return path depends on a parameter."""
        return self.parameter_name is not None

    def is_concrete(self) -> bool:
        """Returns True if this return path is a concrete value."""
        return self.concrete_type is not None


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
            self.variables[-1][name.lexeme] = Type(
                function,
                make_internal_token(name.lexeme),
                parameters=function.parameters,
            )
            self.variables[-1][name.lexeme].return_type = self.variables[-1][
                name.lexeme
            ]

        for name, func in ALL_FUNCTIONS.items():
            if name.lexeme not in self.variables[-1]:
                function = func(interpreter)
                return_type = self.variables[-1].get(function.return_token.lexeme)
                self.variables[-1][name.lexeme] = Type(
                    func(interpreter),
                    make_internal_token(name.lexeme),
                    parameters=function.parameters,
                    return_type=return_type,
                )

            function = self.variables[-1][name.lexeme].klass
            methods = getattr(function, "methods", {})
            if not methods:
                continue

            method_types = {}
            instance = function.instance_class(interpreter)
            for method_name, method_class in methods.items():
                method = method_class(instance)
                type_ = self.variables[-1].get(method.return_token.lexeme)
                method_types[method_name] = Type(
                    method,
                    make_internal_token(method_name),
                    parameters=method.parameters,
                    return_type=type_,
                )
            self.variables[-1][name.lexeme].methods = method_types

        # Store VarArgs type for use with varargs parameters
        self.varargs_type = self.variables[-1].get("VarArgs")

        for name in INTERNAL_TYPES:
            # These types are reserved to internal functionalities
            self.variables[-1].pop(name.lexeme)

        self.current_function: Token | None = None
        self.current_function_return_types = []
        self.current_function_return_paths: list[ReturnPath] = []
        self.current_class: Token | None = None
        self.current_method_calls_super = False
        self.current_function_parameters: list[Parameter] = []
        # Track which loop variables come from iterating over varargs parameters
        # Maps loop variable name -> varargs parameter
        self.loop_var_to_varargs: dict[str, Parameter] = {}

    def get_current_function_parameters(self) -> list[Parameter]:
        return (
            self.current_function_parameters if self.current_function_parameters else []
        )

    def find_parameter(self, name: str) -> Parameter | None:
        for param in self.current_function_parameters:
            if param.name.lexeme == name:
                return param
        return None

    def format_type_name(self, type_: Type) -> str:
        # Parameter types (used inside function definitions)
        if type_.klass is object:
            return f"<parameter {type_.token.lexeme}>"

        # Built-in internal types (Int, String, etc.)
        if isinstance(type_.klass, type) and issubclass(type_.klass, BaseInternalClass):
            return f"<instanceof {type_.klass.name.lexeme}>"

        # Internal classes
        if isinstance(type_.klass, ClassCallable):
            return f"<class {type_.token.lexeme}>"

        # Internal functions
        if isinstance(type_.klass, FunctionCallable):
            return f"<function {type_.token.lexeme}>"

        # User-defined classes and functions
        if hasattr(type_.klass, "name"):
            return f"<class {type_.klass.name.lexeme}>"

        # Fallback
        return str(type_.klass)

    def validate_structural_requirements(
        self,
        obj_type: Type,
        required_attributes: list[Token],
        required_methods: list[Token],
        call_token: Token,
    ):
        for attr in required_attributes:
            if attr.lexeme not in obj_type.methods and not self.get_method_from_super(
                obj_type, attr
            ):
                self.parser_error(
                    call_token,
                    f"{self.format_type_name(obj_type)} does not have required attribute '{attr.lexeme}'.",
                )

        for method in required_methods:
            if method.lexeme not in obj_type.methods and not self.get_method_from_super(
                obj_type, method
            ):
                self.parser_error(
                    call_token,
                    f"{self.format_type_name(obj_type)} does not have required method '{method.lexeme}'.",
                )

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
                superclass.token.lexeme == expected.lexeme
                for superclass in value.superclasses
            )

        return False

    def get_common_type(self, old_type: Type | Deferred, new_type: Type | Deferred):
        if isinstance(old_type, Deferred):
            return new_type

        if isinstance(new_type, Deferred):
            return old_type

        # If both are parameter types, they're compatible
        if old_type.klass is object and new_type.klass is object:
            return old_type

        # If one is a parameter and one is concrete, keep the parameter type
        # This will be resolved at call time
        if old_type.klass is object:
            return old_type
        if new_type.klass is object:
            return new_type

        if (
            isinstance(old_type.klass, type)
            and isinstance(new_type.klass, type)
            and issubclass(old_type.klass, BaseInternalClass)
            and issubclass(new_type.klass, BaseInternalClass)
            and old_type.klass.name == new_type.klass.name
        ):
            return new_type
        if (
            isinstance(old_type.klass, type)
            and issubclass(old_type.klass, BaseInternalClass)
            or isinstance(new_type.klass, type)
            and issubclass(new_type.klass, BaseInternalClass)
        ):
            raise TypeError

        if isinstance(old_type.klass, FunctionCallable) and isinstance(
            new_type.klass, FunctionCallable
        ):
            return new_type
        if isinstance(old_type.klass, FunctionCallable) or isinstance(
            new_type.klass, FunctionCallable
        ):
            raise TypeError

        if isinstance(old_type.klass, ClassCallable) and isinstance(
            new_type.klass, ClassCallable
        ):
            if old_type.klass.name == new_type.klass.name:
                return new_type

            for class_name_2 in (
                new_type.klass.name,
                *(superclass.token.lexeme for superclass in new_type.superclasses),
            ):
                for class_name_1 in (
                    old_type.klass.name,
                    *(superclass.token.lexeme for superclass in old_type.superclasses),
                ):
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
        previous_return_paths = self.current_function_return_paths
        self.current_function_return_paths = []
        previous_parameters = self.current_function_parameters
        self.current_function_parameters = statement.params

        self.begin_scope()
        self.set_parameters(statement.params)
        self.check_many(statement.body)

        # Collect return paths for this function
        return_paths = self.current_function_return_paths.copy()

        try:
            ret_type = self.get_return_type()
            if ret_type is None and self.current_class is not None:
                # -1 is function scope, -2 is class scope, -3 is outside scope where class is defined
                ret_type = self.variables[-3].get(self.current_class.lexeme)
        except TypeError:
            self.parser_error(
                statement.token, "Multiple return types found for function."
            )
        self.end_scope()

        self.current_function = previous_function
        self.current_function_return_types = previous_return_types
        self.current_function_return_paths = previous_return_paths
        self.current_function_parameters = previous_parameters

        return Type(
            FunctionCallable(
                statement.token,
                Lambda(
                    statement.token,
                    statement.params,
                    statement.body,
                ),
                self.interpreter.environment,
            ),
            statement.token,
            statement.params,
            return_type=ret_type,
            calls_super=self.current_method_calls_super,
            return_paths=return_paths,
        )

    def set_parameters(self, parameters: list[Parameter]):
        for parameter in parameters:
            if parameter.is_varargs and self.varargs_type:
                # VarArgs parameters get the VarArgs type with its methods
                self.variables[-1][parameter.name.lexeme] = self.varargs_type
            else:
                # Regular parameters get a generic object type for structural typing
                self.variables[-1][parameter.name.lexeme] = Type(object, parameter.name)

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

    def resolve_return_type_from_paths(
        self,
        return_paths: list,
        parameters: list[Parameter],
        arguments: list,
        callee_token,
    ) -> Type:
        """
        Resolve the actual return type based on return paths and actual arguments.
        Also detects conflicting return types.
        """
        resolved_types = []

        for path in return_paths:
            if path.is_concrete():
                # Concrete return type
                resolved_types.append(path.concrete_type)
            elif path.is_parameter_dependent():
                # Find the argument for this parameter
                param_index = None
                for i, param in enumerate(parameters):
                    if param.name.lexeme == path.parameter_name:
                        param_index = i
                        break

                if param_index is None or param_index >= len(arguments):
                    continue

                arg = arguments[param_index]
                arg_type = self.check(arg.value if isinstance(arg, Argument) else arg)

                # Apply method chain if any
                current_type = arg_type
                for method_name in path.method_chain:
                    if current_type and hasattr(current_type, "methods"):
                        method_type = current_type.methods.get(method_name)
                        if method_type and hasattr(method_type, "return_type"):
                            current_type = method_type.return_type
                        else:
                            # Method not found, can't determine type
                            current_type = None
                            break

                if current_type:
                    resolved_types.append(current_type)

        # Check if all resolved types are compatible
        if not resolved_types:
            return None

        common_type = resolved_types[0]
        for type_ in resolved_types[1:]:
            try:
                common_type = self.get_common_type(common_type, type_)
            except TypeError:
                # Incompatible types - this is an error
                if callee_token:
                    # Extract the actual token from Variable if needed
                    token = (
                        callee_token.name
                        if hasattr(callee_token, "name")
                        else callee_token
                    )
                    self.parser_error(
                        token, "Multiple return types found for function."
                    )
                raise TypeError("Incompatible return types")

        return common_type

    def validate_init_with_arguments(
        self, init_method: Type, arguments: list, callee_token
    ):
        """
        Validate that an init method body is compatible with the actual argument types.
        This checks for issues like assigning a parameter then a different type to attributes.
        """
        if not hasattr(init_method.klass, "declaration"):
            return

        declaration = init_method.klass.declaration
        if not hasattr(declaration, "body") or not hasattr(declaration, "params"):
            return

        # Build a mapping of parameter names to actual argument types
        param_type_map = {}
        for i, param in enumerate(declaration.params):
            if i < len(arguments):
                arg = arguments[i]
                arg_type = self.check(arg.value if isinstance(arg, Argument) else arg)
                param_type_map[param.name.lexeme] = arg_type

        # Check Set expressions in the init body for parameter usage
        self.validate_body_with_param_types(declaration.body, param_type_map)

    def validate_body_with_param_types(self, statements, param_type_map: dict):
        """
        Check statements for Set expressions that might conflict with parameter types.
        Validates assignments where the attribute was previously set to a parameter type.
        """
        from .statements import ExpressionStatement
        from .expressions import Set, Variable, Literal

        # Track attribute types as we process assignments
        attribute_types = {}

        for statement in statements:
            # Handle expression statements that contain Set expressions
            if isinstance(statement, ExpressionStatement):
                expr = statement.expression
                if isinstance(expr, Set):
                    # Determine the value type
                    value_type = None
                    if (
                        isinstance(expr.value, Variable)
                        and expr.value.name.lexeme in param_type_map
                    ):
                        # Assigning a parameter to an attribute
                        value_type = param_type_map[expr.value.name.lexeme]
                    elif isinstance(expr.value, Literal):
                        # For literals, we can safely get their type without recursion
                        value_type = self.check(expr.value)
                    # Skip complex expressions to avoid scope issues

                    if value_type is not None:
                        attr_key = expr.name.lexeme

                        # Check if we're redefining an attribute with an incompatible type
                        if attr_key in attribute_types:
                            previous_type = attribute_types[attr_key]
                            try:
                                # Try to get common type
                                self.get_common_type(previous_type, value_type)
                            except TypeError:
                                # Incompatible types
                                previous_type_name = self.format_type_name(
                                    previous_type
                                )
                                new_type_name = self.format_type_name(value_type)
                                self.parser_error(
                                    expr.name,
                                    f"Cannot redefine attribute of type {previous_type_name} to type {new_type_name}.",
                                )
                        else:
                            attribute_types[attr_key] = value_type

    def visit_call(self, expression):
        # Try to handle special cases that can be resolved early
        early_return = self._try_handle_special_call_cases(expression)
        if early_return is not None:
            return early_return

        # Resolve the callee type
        callee_type = self._resolve_callee_type(expression)
        if callee_type is None:
            return None

        # Get and validate parameters
        parameters = self._get_and_validate_parameters(expression, callee_type)

        # Validate argument types against parameter requirements
        self._validate_argument_types(expression, parameters)

        # Validate init method for class constructors
        self._validate_class_constructor(expression, callee_type)

        # Resolve and return the return type
        return self._resolve_return_type(expression, callee_type)

    def _try_handle_special_call_cases(self, expression):
        """Handle special call cases that can be resolved early."""
        # Track method calls on parameters
        if self._is_method_call_on_parameter(expression):
            param = self.find_parameter(expression.callee.obj.name.lexeme)
            if param is not None:
                param.methods_called.append(expression.callee.name)
            return Type(object, expression.callee.name)

        # Track method calls on loop variables from varargs parameters
        if self._is_method_call_on_varargs_loop_var(expression):
            varargs_param = self.loop_var_to_varargs[expression.callee.obj.name.lexeme]
            varargs_param.methods_called.append(expression.callee.name)
            return Type(object, expression.callee.name)

        # Handle recursive calls
        if self._is_recursive_call(expression):
            return Deferred(expression.callee.name)

        return None

    def _is_method_call_on_parameter(self, expression):
        """Check if this is a method call on a parameter."""
        return (
            isinstance(expression.callee, Get)
            and isinstance(expression.callee.obj, Variable)
            and self.current_function is not None
            and expression.callee.obj.name.lexeme
            in [p.name.lexeme for p in self.get_current_function_parameters()]
        )

    def _is_method_call_on_varargs_loop_var(self, expression):
        """Check if this is a method call on a loop variable from varargs."""
        return (
            isinstance(expression.callee, Get)
            and isinstance(expression.callee.obj, Variable)
            and expression.callee.obj.name.lexeme in self.loop_var_to_varargs
        )

    def _is_recursive_call(self, expression):
        """Check if this is a recursive function call."""
        return (
            self.current_function is not None
            and hasattr(expression.callee, "name")
            and (
                self.current_class is None
                or not isinstance(expression.callee, Variable)
                and isinstance(expression.callee.obj, Get)
                and expression.callee.obj.name == "self"
            )
            and expression.callee.name.lexeme == self.current_function.lexeme
        )

    def _resolve_callee_type(self, expression):
        """Resolve the type of the callee being called."""
        callee_type = self.check(expression.callee)

        if callee_type is None:
            try:
                if hasattr(expression.callee, "name"):
                    callee_type = self.get_type(expression.callee.name, False)
                    expression.callee.type_ = callee_type
            except (AttributeError, TypeError):
                pass

        if callee_type is None:
            # For Get expressions (method calls), this is handled in visit_get
            if isinstance(expression.callee, Get):
                return Type(object, expression.callee.name)

            if hasattr(expression.callee, "name"):
                self.parser_error(
                    expression.callee.name,
                    f"Function {expression.callee.name.lexeme} not found.",
                )
            return None

        return callee_type

    def _get_and_validate_parameters(self, expression, callee_type):
        """Get parameters and validate argument count."""
        # If the callee type is a generic object (parameter type), we can't validate parameters
        if callee_type.klass is object:
            return []

        try:
            parameters = self.get_parameters(
                callee_type.klass, expression.arguments, callee_type.parameters
            )
        except InternalError as e:
            if hasattr(expression.callee, "name"):
                self.parser_error(
                    expression.callee.name, str(e).format(expression.callee.name.lexeme)
                )
            # This line won't be reached due to parser_error raising, but for clarity
            raise
        except (AttributeError, TypeError):
            # Handle cases where klass doesn't have the expected methods
            return []

        callee_name = (
            expression.callee.keyword
            if isinstance(expression.callee, Super)
            else getattr(expression.callee, "name", expression.callee)
        )
        self.validate_parameters(
            expression.arguments, parameters, callee_type.klass, callee_name
        )

        return parameters

    def _validate_argument_types(self, expression, parameters):
        """Validate that arguments have the required methods/attributes."""
        params_to_check = parameters
        if hasattr(self.check(expression.callee), "klass"):
            callee_type = self.check(expression.callee)
            if hasattr(callee_type.klass, "declaration") and isinstance(
                callee_type.klass.declaration, Lambda
            ):
                params_to_check = callee_type.klass.declaration.params

        # Check if the last parameter is varargs and has requirements
        has_varargs = params_to_check and params_to_check[-1].is_varargs
        varargs_param = params_to_check[-1] if has_varargs else None

        # Validate regular parameters
        validated_args = self._validate_regular_parameters(
            expression.arguments, params_to_check
        )

        # Validate varargs parameters
        if has_varargs and (
            varargs_param.attributes_accessed or varargs_param.methods_called
        ):
            self._validate_varargs_parameters(
                expression.arguments, params_to_check, varargs_param, validated_args
            )

    def _validate_regular_parameters(self, arguments, params_to_check):
        """Validate arguments against regular parameters."""
        validated_args = set()

        for i, (arg, param) in enumerate(zip(arguments, params_to_check)):
            # Skip validation for unpacked arguments
            arg_value = arg.value if isinstance(arg, Argument) else arg
            if isinstance(arg_value, Unpack):
                continue

            if param.attributes_accessed or param.methods_called:
                arg_type = self.check(arg)
                if arg_type:
                    arg_token = self.get_arg_name(arg)
                    self.validate_structural_requirements(
                        arg_type,
                        param.attributes_accessed,
                        param.methods_called,
                        arg_token,
                    )

            validated_args.add(i)

        return validated_args

    def _validate_varargs_parameters(
        self, arguments, params_to_check, varargs_param, validated_args
    ):
        """Validate all arguments passed to varargs parameter."""
        # Get the index where varargs starts (after regular params)
        regular_param_count = len([p for p in params_to_check if not p.is_varargs])

        # Validate all arguments from regular_param_count onwards
        for i in range(regular_param_count, len(arguments)):
            if i in validated_args:
                continue

            arg = arguments[i]
            arg_value = arg.value if isinstance(arg, Argument) else arg

            # Skip unpacked arguments
            if isinstance(arg_value, Unpack):
                continue

            arg_type = self.check(arg)
            if arg_type:
                arg_token = self.get_arg_name(arg)
                self.validate_structural_requirements(
                    arg_type,
                    varargs_param.attributes_accessed,
                    varargs_param.methods_called,
                    arg_token,
                )

    def _validate_class_constructor(self, expression, callee_type):
        """Validate init method for class constructors."""
        if isinstance(callee_type.klass, ClassCallable):
            init_method = callee_type.methods.get("init")
            if init_method:
                if hasattr(init_method.klass, "declaration"):
                    self.validate_init_with_arguments(
                        init_method,
                        expression.arguments,
                        expression.callee
                        if hasattr(expression.callee, "name")
                        else None,
                    )

    def _resolve_return_type(self, expression, callee_type):
        """Resolve the return type of the call."""
        # Resolve parameter-dependent return types using return paths
        if callee_type.return_paths:
            return self.resolve_return_type_from_paths(
                callee_type.return_paths,
                callee_type.parameters,
                expression.arguments,
                expression.callee if hasattr(expression.callee, "name") else None,
            )

        # Fallback to original logic for legacy support
        return_type = callee_type.return_type
        if return_type and return_type.klass is object:
            # The return type is a parameter - find which one and use the argument type
            param_name = return_type.token.lexeme
            for i, param in enumerate(callee_type.parameters):
                if param.name.lexeme == param_name and i < len(expression.arguments):
                    arg = expression.arguments[i]
                    arg_type = self.check(
                        arg.value if isinstance(arg, Argument) else arg
                    )
                    return arg_type

        return return_type

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
        if isinstance(arg_structure_value, Unpack):
            return arg_structure_value.operator
        return arg_structure_value.token

    def calculate_expanded_argument_count(
        self,
        arguments: list[Type],
    ) -> tuple[int | None, list[int | None]]:
        """
        Calculate the total argument count after unpacking.
        Returns (total_count, individual_counts) where:
        - total_count: the total number of arguments, or None if any are unknown
        - individual_counts: list with count for each arg (None if unknown)

        For each argument:
        - Regular args contribute 1
        - Unpacked args contribute their size if determinable, None otherwise
        """
        individual_counts = []
        total_count = 0
        has_unknown = False

        for arg in arguments:
            arg_value = arg.value if isinstance(arg, Argument) else arg

            if isinstance(arg_value, Unpack):
                # For now, we can't reliably determine the size of unpacked iterables
                # at compile time. This could be enhanced in the future for specific cases.
                individual_counts.append(None)
                has_unknown = True
            else:
                # Regular argument counts as 1
                individual_counts.append(1)
                total_count += 1

        if has_unknown:
            return (None, individual_counts)

        return (total_count, individual_counts)

    def get_parameters(
        self,
        klass: InternalCallable,
        arguments: list[Type],
        parameters: list[Parameter],
    ) -> list[Parameter]:
        parameters = parameters.copy()
        lower_arity, upper_arity = self.get_arity(klass)
        arguments_length = len(arguments)

        # Try to calculate the expanded argument count
        expanded_count, individual_counts = self.calculate_expanded_argument_count(
            arguments
        )

        # Check if we have any unpacking
        has_unpack = any(count is None for count in individual_counts)

        # If we can determine the exact count, validate it
        if expanded_count is not None:
            if lower_arity > expanded_count or upper_arity < expanded_count:
                raise InternalError(
                    f"Expected between {lower_arity} and {upper_arity} arguments in call to {{}} but got {expanded_count}."
                )
            arguments_length = expanded_count
        elif has_unpack:
            # We have unpacking but can't determine the count
            # We can still validate minimum count: sum of known args
            known_count = sum(c for c in individual_counts if c is not None)

            # If the function has no varargs, we need exact match
            # Check if there are any varargs in parameters
            has_varargs = parameters and parameters[-1].is_varargs

            if not has_varargs:
                # Non-varargs function with unpacking
                # We can only check minimum: known args shouldn't exceed max
                if known_count > upper_arity:
                    raise InternalError(
                        f"Expected between {lower_arity} and {upper_arity} arguments in call to {{}} but got at least {known_count} (with unpacking)."
                    )
                # We can't validate lower bound since unpacked might have more

        if not parameters:
            return []

        if parameters[-1].is_varargs:
            # VarArgs is not added until we're certain it is required, since it could be empty
            vararg = parameters[-1]
            parameters = parameters[:-1]
            # Only add varargs if we can determine the count
            if expanded_count is not None:
                for _ in range(arguments_length - (len(parameters))):
                    parameters.append(vararg)
            else:
                # With unpacking we can't determine, so just add one vararg
                parameters.append(vararg)

        return parameters

    def get_arity(self, klass: InternalCallable) -> tuple[int, int]:
        minimum = klass.lower_arity()
        maximum = klass.upper_arity()

        return minimum, maximum

    def validate_parameters(
        self,
        all_arguments: list[Argument],
        parameters: list[Parameter],
        callee_klass: InternalCallable = None,
        callee_name: Token = None,
    ):
        arguments = [arg for arg in all_arguments if arg.name is None]
        argument_names = [self.get_arg_name(arg) for arg in arguments]
        argument_types = self.check_many(arguments)
        named_arguments = {
            arg.name.lexeme: arg for arg in all_arguments if arg.name is not None
        }

        if len(arguments) < len(parameters):
            for parameter in parameters[len(arguments) :]:
                if parameter.name.lexeme in named_arguments:
                    name = self.get_arg_name(named_arguments[parameter.name.lexeme])
                    type_ = self.check(named_arguments[parameter.name.lexeme])
                else:
                    # Parameter with default value - skip validation
                    continue

                argument_names.append(name)
                argument_types.append(type_)

        # Validate types for built-in methods that have allowed_types
        # For classes, check the init method; for methods, check the method itself
        method_to_check = None
        if callee_klass and hasattr(callee_klass, "internal_find_method"):
            try:
                # This is a class, get its init method and bind it to an instance
                init_method_class = callee_klass.internal_find_method("init")
                instance = callee_klass.instance_class(self.interpreter)
                method_to_check = init_method_class.bind(instance)
            except Exception:
                pass
        elif callee_klass:
            # This is already a method
            method_to_check = callee_klass

        if method_to_check and hasattr(method_to_check, "allowed_types"):
            try:
                allowed_types = method_to_check.allowed_types
            except AttributeError:
                allowed_types = None
            if allowed_types:
                # Check if this is a varargs parameter
                is_varargs = (
                    parameters and parameters[0].is_varargs if parameters else False
                )

                # For varargs, check all arguments; otherwise just the first
                args_to_check = argument_types if is_varargs else argument_types[:1]
                names_to_check = argument_names if is_varargs else argument_names[:1]

                for arg_type, arg_name in zip(args_to_check, names_to_check):
                    # Check if the argument type matches any allowed type
                    type_match = any(
                        self.validate_type(arg_type, allowed_type)
                        for allowed_type in allowed_types
                    )

                    if not type_match:
                        # Generate error message
                        if len(allowed_types) == 1:
                            expected_str = allowed_types[0].lexeme
                        else:
                            expected_str = " or ".join(t.lexeme for t in allowed_types)

                        actual_type = (
                            arg_type.klass.name.lexeme
                            if hasattr(arg_type.klass, "name")
                            else str(arg_type.klass)
                        )
                        param_name = (
                            parameters[0].name.lexeme if parameters else "parameter"
                        )
                        func_name = (
                            callee_name.lexeme
                            if callee_name and hasattr(callee_name, "lexeme")
                            else str(callee_klass)
                        )

                        self.parser_error(
                            arg_name,
                            f"Expected {expected_str} but got {actual_type} for parameter {param_name} in call to {func_name}.",
                        )

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
                previous_type_name = self.format_type_name(previous_type)
                new_type_name = self.format_type_name(new_type)
                self.parser_error(
                    expression.name.name,
                    f"Cannot redefine variable of type {previous_type_name} to type {new_type_name}.",
                )
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
        methods = {m.token.lexeme: m.klass for m in method_types}
        klass.methods.update(methods)
        init = method_types_dict.get("init") or self.get_method_from_super(
            type_, make_internal_token("init")
        )
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
            previous_type_name = self.format_type_name(previous_type)
            new_type_name = self.format_type_name(new_type)
            self.parser_error(
                expression.name,
                f"Cannot redefine attribute of type {previous_type_name} to type {new_type_name}.",
            )
        else:
            obj.methods[expression.name.lexeme] = type_
            return type_

    def visit_get(self, expression):
        obj = self.check(expression.obj)

        # If we're accessing an attribute on a parameter, track it
        if (
            isinstance(expression.obj, Variable)
            and self.current_function is not None
            and expression.obj.name.lexeme
            in [p.name.lexeme for p in self.get_current_function_parameters()]
        ):
            # Track the attribute access on the parameter
            param = self.find_parameter(expression.obj.name.lexeme)
            if param is not None:
                param.attributes_accessed.append(expression.name)

            # For parameter attribute access, return a generic object type since we don't know the type yet
            return Type(object, expression.name)

        # If we're accessing an attribute on a loop variable that comes from a varargs parameter, track it
        if (
            isinstance(expression.obj, Variable)
            and expression.obj.name.lexeme in self.loop_var_to_varargs
        ):
            varargs_param = self.loop_var_to_varargs[expression.obj.name.lexeme]
            varargs_param.attributes_accessed.append(expression.name)
            # Return a generic object type since we don't know the element type yet
            return Type(object, expression.name)

        # Handle None type (void)
        if obj is None:
            return None

        ret = obj.methods.get(expression.name.lexeme)

        if ret is None:
            ret = self.get_method_from_super(obj, expression.name)

        # TODO: With map-based init, we can't validate fields at type-check time
        # We need to analyze the Map returned by init to extract field names
        # For now, skip this validation to allow map-based init to work
        # if ret is None and not isinstance(obj.klass, type):
        #     self.parser_error(
        #         expression.name,
        #         f"Attribute {expression.name.lexeme} not found for class {obj.klass.name.lexeme}.",
        #     )

        return ret

    def get_method_from_super(self, type_: Type, name: Token):
        for superclass in type_.superclasses:
            if name.lexeme in superclass.methods:
                ret = superclass.methods[name.lexeme]
                if (
                    ret is None
                    and (method := superclass.methods[name.lexeme])
                    and method.calls_super
                ):
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

    def analyze_return_path(self, expression) -> ReturnPath:
        """Analyze an expression to determine its return path characteristics."""
        # Direct parameter return: return arg_1
        if isinstance(expression, Variable):
            param = self.find_parameter(expression.name.lexeme)
            if param is not None:
                return ReturnPath(parameter_name=expression.name.lexeme)

        # Method call chain on parameter: return arg_1.toString() or arg_1.add(1).toString()
        if isinstance(expression, Call) and isinstance(expression.callee, Get):
            # Extract the chain of method calls
            method_chain = []
            current = expression

            while isinstance(current, Call) and isinstance(current.callee, Get):
                method_chain.insert(0, current.callee.name.lexeme)
                current = current.callee.obj

            # Check if the base is a parameter
            if isinstance(current, Variable):
                param = self.find_parameter(current.name.lexeme)
                if param is not None:
                    return ReturnPath(
                        parameter_name=current.name.lexeme, method_chain=method_chain
                    )

        # Single method call on parameter: Could also be Get without Call
        if isinstance(expression, Get):
            if isinstance(expression.obj, Variable):
                param = self.find_parameter(expression.obj.name.lexeme)
                if param is not None:
                    return ReturnPath(
                        parameter_name=expression.obj.name.lexeme,
                        method_chain=[expression.name.lexeme],
                    )

        # Concrete type return - get the type
        type_ = self.check(expression)
        return ReturnPath(concrete_type=type_)

    def visit_return_statement(self, statement):
        ret = self.check(statement.value)
        self.current_function_return_types.append(ret)

        # Also track the return path
        return_path = self.analyze_return_path(statement.value)
        self.current_function_return_paths.append(return_path)

        return ret

    def visit_if_expression(self, expression):
        then_type = self.check(expression.then_branch)
        else_type = self.check(expression.else_branch)

        try:
            return self.get_common_type(then_type, else_type)
        except TypeError:
            previous_type_name = self.format_type_name(then_type)
            new_type_name = self.format_type_name(else_type)
            self.parser_error(
                expression.keyword,
                f"Got different return types in if expression: {previous_type_name} and {new_type_name}.",
            )

    def visit_argument(self, expression):
        return self.check(expression.value)

    def visit_unary(self, expression):
        if expression.operator.type_ == TokenType.BANG:
            return self.variables[0]["Bool"]

        right_type = self.check(expression.right)

        try:
            return right_type.methods["negate"].return_type
        except KeyError:
            self.parser_error(
                expression.operator,
                f"{right_type.token.lexeme} does not implement the negate method.",
            )

    def visit_unpack(self, expression):
        """
        Type check an unpack expression.
        The expression must be iterable (have an iterate method).
        Returns a special marker that indicates this is an unpacked iterable.
        """
        iterable_type = self.check(expression.expression)

        # Check if the type has an iterate method
        if "iterate" not in iterable_type.methods:
            self.parser_error(
                expression.operator,
                f"{iterable_type.token.lexeme} is not iterable (no iterate method).",
            )

        # Return a marker type that indicates this is unpacked
        # We'll use a generic object type with a special flag
        # In practice, the unpacked values could be of any type the iterator yields
        return Type(object, expression.operator)

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
                raise ValueError(
                    "Max, you forgot to implement something!", expression.operator
                )

        # If left side is a parameter type, defer checking to call site
        if left_type.klass is object:
            # Track that this parameter needs the method
            if isinstance(expression.left, Variable):
                param = self.find_parameter(expression.left.name.lexeme)
                if param is not None:
                    method_token = make_internal_token(method)
                    param.methods_called.append(method_token)
            # Return object type since we don't know the result type yet
            return Type(object, expression.operator)

        obj = left_type.methods.get(method)
        if obj is None:
            self.parser_error(
                expression.operator,
                f"{self.format_type_name(left_type)} does not implement the {method} method.",
            )

        argument = Argument(None, expression.right)
        method_token = make_internal_token(method)
        self.validate_parameters([argument], obj.parameters, obj.klass, method_token)

        return obj.return_type

    def visit_for_statement(self, statement):
        in_name = self.check(statement.in_name)
        self.begin_scope()
        iterate = in_name.methods.get("iterate")

        if iterate is None:
            self.parser_error(
                statement.keyword,
                f"Cannot iterate over instance of {self.format_type_name(in_name)} that does not implement 'iterate'.",
            )

        next_ = iterate.return_type.methods.get("next")

        if next_ is None:
            self.parser_error(
                statement.keyword,
                f"Cannot get next value from iterator {self.format_type_name(iterate.return_type)} that does not implement 'next'.",
            )

        self.variables[-1][statement.for_name.name.lexeme] = next_.return_type

        # Check if we're iterating over a varargs parameter
        if (
            isinstance(statement.in_name, Variable)
            and self.current_function is not None
        ):
            param = self.find_parameter(statement.in_name.name.lexeme)
            if param is not None and param.is_varargs:
                # Track that this loop variable comes from iterating over a varargs parameter
                self.loop_var_to_varargs[statement.for_name.name.lexeme] = param

        self.check_many(statement.body)

        # Clean up the loop variable tracking when exiting the for loop scope
        if statement.for_name.name.lexeme in self.loop_var_to_varargs:
            del self.loop_var_to_varargs[statement.for_name.name.lexeme]

        self.end_scope()

    def visit_if_statement(self, statement):
        self.check(statement.then_branch)

        if statement.else_branch is not None:
            self.check(statement.else_branch)

    def visit_logical(self, expression):
        # TODO: Validate logical expressions
        return super().visit_logical(expression)

    def visit_while_statement(self, statement):
        self.check(statement.body)
