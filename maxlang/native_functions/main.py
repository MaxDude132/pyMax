from __future__ import annotations
from typing import TYPE_CHECKING

from maxlang.parse.callable import InternalCallable, ClassCallable, InstanceCallable
from maxlang.errors import InternalError
from maxlang.parse.expressions import Lambda

if TYPE_CHECKING:
    from maxlang.parse.interpreter import Interpreter


def format_class_name(name: str):
    return f"<{name}>"


class BaseInternalFunction(InternalCallable):
    name = ""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        if hasattr(self, "init"):
            self.init()

    @property
    def declaration(self):
        return Lambda([], [])


class BaseInternalMethod(InternalCallable):
    name = ""

    @property
    def declaration(self):
        return Lambda([], [])

    def get_class(self):
        return self.instance.klass

    @property
    def class_name(self):
        return format_class_name(f"{self.get_class().name}.{self.name}")

    def return_self(self):
        return self.instance

    @classmethod
    def bind(cls, instance: BaseInternalInstance):
        return cls(instance)

    def __init__(self, instance: BaseInternalClass):
        self.instance = instance

    def __str__(self):
        return f"<method '{self.name}' of class '{self.instance.class_name}'>"


class BaseInternalAttribute(InternalCallable):
    name = ""

    @property
    def class_name(self):
        return format_class_name(f"{self.get_class().name}.{self.name}")

    def get_class(self):
        return self.instance.klass

    def __init__(self, instance: BaseInternalClass):
        self.instance = instance

    def __str__(self):
        return f"<attribute '{self.name}' of class '{self.instance.name}'>"


# Methods shared by all class instances
class SharedIsNotTrue(BaseInternalMethod):
    name = "isNotTrue"

    def call(self, interpreter, arguments):
        from .BaseTypes.Bool import BoolInstance

        try:
            bool_value = self.instance.internal_find_method("isTrue").call(
                interpreter, []
            )
            return BoolInstance(interpreter).set_value(not bool_value.value)
        except KeyError:
            raise InternalError(
                f"class {self.class_name} does not implement the isTrue method."
            )


class SharedIsInstance(BaseInternalMethod):
    name = "isInstance"

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
    name = ""
    FIELDS = ()
    __COMMON_FIELDS = (
        SharedIsNotTrue,
        SharedIsInstance,
    )

    def get_class(self):
        return self

    @property
    def class_name(self):
        return format_class_name("class " + self.get_class().name)

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.methods = {m.name: m for m in self.FIELDS + self.__COMMON_FIELDS}
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
        return self.methods[name]

    def check_arity(self, arg_count):
        return arg_count >= self.lower_arity() and arg_count <= self.upper_arity()

    def upper_arity(self):
        return 0

    def lower_arity(self):
        return 0

    def parameters(self):
        return []


class BaseInternalInstance(InstanceCallable):
    CLASS = BaseInternalClass

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.klass = self.interpreter.environment.internal_get(self.CLASS.name)

    @property
    def class_name(self):
        return format_class_name(self.get_class().name)

    def internal_find_method(self, name):
        return self.klass.internal_find_method(name).bind(self)

    def get_class(self):
        return self.klass


def is_instance(interpreter: Interpreter, instance: InstanceCallable, *class_names: str) -> bool:
    for class_name in class_names:
        klass = interpreter.environment.internal_get(class_name)
        val = instance.internal_find_method("isInstance").call(
            interpreter, [klass]
        ).value
        if val:
            return True
        
    return False
