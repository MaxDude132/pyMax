from __future__ import annotations
from typing import TYPE_CHECKING

from maxlang.parse.callable import InternalCallable, ClassCallable, InstanceCallable
from maxlang.errors import InternalError
from maxlang.parse.expressions import Lambda, Parameter
from maxlang.lex import Token, TokenType

if TYPE_CHECKING:
    from maxlang.parse.interpreter import Interpreter


def format_class_name(name: str):
    return f"<{name}>"


def make_internal_token(string: str) -> Token:
    return Token(TokenType.IDENTIFIER, string, None, -1)


class BaseInternalFunction(InternalCallable):
    name: Token

    def __init__(self, interpreter):
        self.interpreter = interpreter
        if hasattr(self, "init"):
            self.init()

    @property
    def parameters(self):
        return []

    @property
    def declaration(self):
        return Lambda(
            Token(TokenType.IDENTIFIER, self.name, None, -1), self.parameters, []
        )

    @property
    def return_token(self) -> Token:
        from .BaseTypes.Void import VoidClass

        return VoidClass.name


class BaseInternalMethod(InternalCallable):
    name: Token

    @property
    def parameters(self) -> list[Parameter]:
        return []

    @property
    def allowed_types(self) -> list[Token]:
        return []

    @property
    def declaration(self):
        return Lambda(
            Token(TokenType.IDENTIFIER, self.name, None, -1), self.parameters, []
        )

    def lower_arity(self):
        return len(
            [parameter for parameter in self.parameters if not parameter.is_varargs]
        )

    def upper_arity(self):
        return len(self.parameters)

    def get_class(self):
        return self.instance.klass

    @property
    def class_name(self):
        return format_class_name(f"{self.get_class().name.lexeme}.{self.name.lexeme}")

    def return_self(self):
        return self.instance

    @classmethod
    def bind(cls, instance: BaseInternalClass):
        return cls(instance)

    @property
    def return_token(self) -> Token:
        return self.return_self().klass.name

    def __init__(self, instance: BaseInternalInstance):
        self.instance = instance

    def __str__(self):
        return f"<method '{self.name.lexeme}' of class '{self.instance.class_name}'>"


class BaseInternalAttribute(InternalCallable):
    name: Token

    @property
    def class_name(self):
        return format_class_name(f"{self.get_class().name.lexeme}.{self.name.lexeme}")

    def get_class(self):
        return self.instance.klass

    @classmethod
    def bind(cls, instance: BaseInternalClass):
        attribute = cls(instance)
        return attribute.call(attribute.instance.interpreter, [])

    @property
    def return_token(self) -> Token:
        # raise ValueError("Internal Attribute must set a return class.")
        from .BaseTypes.Void import VoidClass

        return VoidClass.name

    def __init__(self, instance: BaseInternalClass):
        self.instance = instance

    def __str__(self):
        return f"<attribute '{self.name.lexeme}' of {self.instance.klass.class_name}>"


# Methods shared by all class instances
class SharedIsNotTrue(BaseInternalMethod):
    name = make_internal_token("isNotTrue")

    def call(self, interpreter, arguments):
        from .BaseTypes.Bool import BoolInstance

        try:
            bool_value = self.instance.internal_find_method("toBool").call(
                interpreter, []
            )
            return BoolInstance(interpreter).set_value(not bool_value.value)
        except KeyError:
            raise InternalError(
                f"class {self.class_name} does not implement the toBool method."
            )


class SharedIsInstance(BaseInternalMethod):
    name = make_internal_token("isInstance")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments: ClassCallable):
        from .BaseTypes.Bool import BoolInstance

        arg = arguments[0]
        if not isinstance(arg, ClassCallable):
            raise InternalError("isInstance only accepts classes as arguments.")

        if isinstance(self.instance, arg.instance_class):
            return BoolInstance(interpreter).set_value(True)

        for klass in self.instance.klass.superclasses:
            if klass is arg:
                return BoolInstance(interpreter).set_value(True)

        return BoolInstance(interpreter).set_value(False)


class BaseInternalClass(ClassCallable):
    name: Token
    FIELDS = ()
    _COMMON_FIELDS = (
        SharedIsNotTrue,
        SharedIsInstance,
    )

    def get_class(self):
        return self

    @property
    def class_name(self):
        return format_class_name("class " + self.get_class().name.lexeme)

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.methods = {m.name.lexeme: m for m in self.FIELDS + self._COMMON_FIELDS}
        self.superclasses = []
        if hasattr(self, "init"):
            self.init()

    def call(self, interpreter, arguments):
        instance = self.instance_class(interpreter)
        method = self.internal_find_method("init").bind(instance)

        ret = method.call(interpreter, arguments)
        if ret is not None:
            return ret

        return method.return_self()

    def internal_find_method(self, name: str):
        try:
            return self.methods[name]
        except KeyError:
            raise InternalError(
                f"{self.class_name} does not implement the '{name}' method."
            )

    def check_arity(self, arg_count):
        return arg_count >= self.lower_arity() and arg_count <= self.upper_arity()

    def get_new_instance(self) -> BaseInternalInstance:
        return self.instance_class(self.interpreter)

    def lower_arity(self):
        try:
            return (
                self.internal_find_method("init")
                .bind(self.get_new_instance())
                .lower_arity()
            )
        except InternalError:
            return 0

    def upper_arity(self):
        try:
            return (
                self.internal_find_method("init")
                .bind(self.get_new_instance())
                .upper_arity()
            )
        except InternalError:
            return 0

    @property
    def parameters(self):
        try:
            return (
                self.internal_find_method("init")
                .bind(self.get_new_instance())
                .parameters
            )
        except InternalError:
            return []

    @property
    def return_token(self) -> Token:
        return self.name


class BaseInternalInstance(InstanceCallable):
    CLASS = BaseInternalClass

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.klass = self.interpreter.environment.get(self.CLASS.name)

    @property
    def class_name(self):
        return format_class_name(self.get_class().name.lexeme)

    def internal_find_method(self, name: str):
        return self.klass.internal_find_method(name).bind(self)

    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.interpreter, [])

    def get_class(self):
        return self.klass


def is_instance(
    interpreter: Interpreter, instance: InstanceCallable, *class_names: Token
) -> bool:
    for class_name in class_names:
        klass = interpreter.environment.get(class_name)
        val = (
            instance.internal_find_method("isInstance").call(interpreter, [klass]).value
        )
        if val:
            return True

    return False
