from __future__ import annotations
from typing import Any, TYPE_CHECKING

from .expressions import Lambda, Parameter
from .environment import Environment
from maxlang.lex import Token, TokenType
from maxlang.errors import InterpreterError, InternalError

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Return(Exception):
    def __init__(self, value):
        self.value = value


class InternalCallable:
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any | None:
        pass

    def check_arity(self, arg_count: int) -> bool:
        return arg_count >= self.lower_arity() and arg_count <= self.upper_arity()

    def upper_arity(self) -> int:
        if self.parameters and self.parameters[-1].is_varargs:
            return float("inf")
        return len(self.parameters)

    def lower_arity(self) -> int:
        return len(
            [
                arg
                for arg in self.parameters
                if arg.default is None and not arg.is_varargs
            ]
        )

    @property
    def parameters(self) -> list[Parameter]:
        return []

    def __str__(self) -> str:
        func_name = "".join(
            "_" + char.lower() if char.isupper() else char
            for char in self.__class__.__name__
        ).lstrip("_")
        return f"<function {func_name}>"


class FunctionCallable(InternalCallable):
    def __init__(
        self,
        name: Token | None,
        declaration: Lambda,
        closure: Environment,
        class_instance: InstanceCallable | None = None,
    ):
        self.name = name
        self.declaration = declaration
        self.closure = closure
        self.class_instance = class_instance

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        environment = Environment(self.closure)
        for i, argument in enumerate(arguments):
            environment.define(self.declaration.params[i].name, argument)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as ret:
            if ret.value is None:
                return self.return_self()

            return ret.value

        return self.return_self()

    def bind(self, instance: InstanceCallable) -> FunctionCallable:
        environment = Environment(self.closure)
        environment.define(Token(TokenType.IDENTIFIER, "self", None, -1), instance)
        return FunctionCallable(self.name, self.declaration, environment, instance)

    def return_self(self) -> Any | None:
        if self.class_instance is not None:
            return self.closure.get_at(0, "self")

    @property
    def parameters(self):
        return self.declaration.params

    @property
    def class_name(self):
        if self.class_instance:
            return self.class_instance.class_name

    def __str__(self) -> str:
        if self.class_instance is not None and self.name is not None:
            return f"<method {self.name.lexeme} of class {self.class_instance}>"
        elif self.name is not None:
            return f"<function {self.name.lexeme}>"
        else:
            return "<lambda>"


class ClassCallable(InternalCallable):
    def __init__(
        self,
        name: Token,
        superclasses: list[ClassCallable],
        methods: dict[str, FunctionCallable],
    ):
        self.name = name
        self.superclasses = superclasses
        self.methods = methods

    @property
    def instance_class(self):
        return InstanceCallable

    def call(self, interpreter, arguments) -> InstanceCallable:
        instance = InstanceCallable(self)
        initialiser = self.find_method(Token(TokenType.IDENTIFIER, "init", None, -1))
        if initialiser is not None:
            # Call init and check if it returns a map-like object
            result = initialiser.bind(instance).call(interpreter, arguments)

            # If init returns a map (dict-like with field definitions), use it
            if (
                result is not None
                and hasattr(result, "values")
                and isinstance(result.values, dict)
            ):
                # Map-based init: create instance from returned map
                from maxlang.native_functions.BaseTypes.Map import MapInstance
                from maxlang.native_functions.BaseTypes.String import StringInstance

                if isinstance(result, MapInstance):
                    for key in result._all_keys():
                        try:
                            value = result._get_value(key)
                            # Convert key to string
                            if isinstance(key, StringInstance):
                                field_name = key.value
                            elif hasattr(key, "value"):
                                field_name = str(key.value)
                            else:
                                field_name = str(key)
                            instance.fields[field_name] = value
                        except KeyError:
                            pass
        return instance

    def check_arity(self, arg_count: int) -> bool:
        initialiser = self.find_method(Token(TokenType.IDENTIFIER, "init", None, -1))
        if initialiser is None:
            return arg_count == 0
        return initialiser.check_arity(arg_count)

    def upper_arity(self) -> int:
        initialiser = self.find_method(Token(TokenType.IDENTIFIER, "init", None, -1))
        if initialiser is None:
            return 0
        return initialiser.upper_arity()

    def lower_arity(self) -> int:
        initialiser = self.find_method(Token(TokenType.IDENTIFIER, "init", None, -1))
        if initialiser is None:
            return 0
        return initialiser.lower_arity()

    @property
    def parameters(self):
        initialiser = self.find_method(Token(TokenType.IDENTIFIER, "init", None, -1))
        if initialiser is None:
            return []
        return initialiser.declaration.params

    def find_method(
        self, name: Token, check_supers: bool = True, errored: bool = False
    ) -> FunctionCallable | None:
        if name.lexeme in self.methods:
            return self.methods.get(name.lexeme)

        if not check_supers and not errored and name.lexeme != "init":
            for superclass in self.superclasses:
                value = superclass.find_method(name, errored=True)
                if value is not None:
                    raise InterpreterError(
                        name,
                        f"Method {name.lexeme} found in superclass to one of the superclasses. Inherit from class {superclass.name} to gain access to this field.",
                    )

        value = None
        for superclass in self.superclasses:
            value = superclass.find_method(name, check_supers=False, errored=errored)
            if value is not None:
                return value

    def internal_find_method(self, name: str):
        return self.find_method(Token(TokenType.IDENTIFIER, name, None, -1))

    @property
    def class_name(self):
        return f"<class {self.name.lexeme}>"

    def __str__(self) -> str:
        return self.class_name


class InstanceCopyMethod(InternalCallable):
    """Internal method that provides copy() functionality for user-defined instances."""

    def __init__(self, instance: InstanceCallable):
        self.instance = instance

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any | None:
        """Call copy with field modifications.

        Arguments must be Pair objects (field_name -> value)
        """
        from maxlang.native_functions.BaseTypes.Pair import PairInstance
        from maxlang.native_functions.BaseTypes.String import StringInstance

        modifications = {}
        for arg in arguments:
            if not isinstance(arg, PairInstance):
                raise InterpreterError(
                    Token(TokenType.IDENTIFIER, "copy", None, -1),
                    f"copy() arguments must be Pair objects (field -> value), got {type(arg)}",
                )

            # Extract field name from Pair
            key = arg.first
            if isinstance(key, StringInstance):
                field_name = key.value
            else:
                raise InterpreterError(
                    Token(TokenType.IDENTIFIER, "copy", None, -1),
                    f"Field name must be a String, got {type(key)}",
                )

            modifications[field_name] = arg.second

        return self.instance.copy(**modifications)

    def check_arity(self, arg_count: int) -> bool:
        return True  # Accepts any number of arguments

    def upper_arity(self) -> int:
        return float("inf")

    def lower_arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return f"<method 'copy' of instance {self.instance.class_name}>"


class InstanceCallable(InternalCallable):
    def __init__(self, klass: ClassCallable):
        self.klass = klass
        self.fields: dict[str, InternalCallable] = {}

    def get(self, name: Token):
        if name.lexeme in getattr(self, "fields", ()):
            return self.fields[name.lexeme]

        # Special case for built-in copy method
        if name.lexeme == "copy":
            return InstanceCopyMethod(self)

        method = self.klass.find_method(name)
        if method is not None:
            return method.bind(self)

        raise InterpreterError(name, f"Undefined property '{name.lexeme}'.")

    def internal_find_method(self, name: str):
        try:
            return self.klass.internal_find_method(name).bind(self)
        except (KeyError, AttributeError):
            raise InternalError(
                f"Could not find method {name} on class {self.class_name.lexeme}."
            )

    def copy(self, **modifications):
        """Create new instance with field modifications.

        Args:
            **modifications: Field name -> value pairs

        Returns:
            New InstanceCallable with modified fields

        Raises:
            InterpreterError: If field name not in self.fields
        """
        # Validate all fields exist
        for field_name in modifications:
            if field_name not in self.fields:
                raise InterpreterError(
                    Token(TokenType.IDENTIFIER, field_name, None, -1),
                    f"Cannot modify undefined field '{field_name}'. "
                    f"Class only defines: {', '.join(self.fields.keys())}",
                )

        new_instance = InstanceCallable(self.klass)

        # Shallow copy existing fields (structural sharing)
        new_instance.fields = self.fields.copy()

        # Apply modifications
        for field_name, value in modifications.items():
            new_instance.fields[field_name] = value

        return new_instance

    def set(self, name: Token, value: Any):
        """Set field value (returns new instance).

        This method is called by visit_set in interpreter.
        Returns new instance instead of mutating.
        """
        if name.lexeme not in self.fields:
            raise InterpreterError(
                name,
                f"Cannot set undefined field '{name.lexeme}'. "
                f"Class only defines: {', '.join(self.fields.keys())}",
            )

        return self.copy(**{name.lexeme: value})

    @property
    def class_name(self):
        return self.klass.name.lexeme

    def __str__(self) -> str:
        return f"<instanceof {self.class_name}>"
