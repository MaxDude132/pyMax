from __future__ import annotations

from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, is_instance
from maxlang.errors import InternalError


def set_value(instance: StringInstance, value: str):
    instance.value = value
    return instance


class StringInit(BaseInternalMethod):
    name = "init"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        set_value(self.instance, arguments[0])


class StringAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        from .Float import FloatInstance

        if isinstance(arguments[0], (IntInstance, FloatInstance, StringInstance)):
            return StringInstance(interpreter).set_value(
                self.instance.value + str(arguments[0].value)
            )

        raise InternalError(
            f"Cannot add {self.instance.class_name} and {arguments[0].class_name}"
        )


class StringMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return StringInstance(interpreter).set_value(
                self.instance.value * arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class StringEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], StringClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value == arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class StringIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.value) != 0)


class StringToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        return StringInstance(interpreter).set_value(self.instance.value)


class StringClass(BaseInternalClass):
    name = "String"
    FIELDS = (
        StringInit,
        StringAdd,
        StringMultiply,
        StringEquals,
        StringIsTrue,
        StringToString,
    )

    @property
    def instance_class(self):
        return StringInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        return StringInstance(interpreter).set_value(arguments[0])


class StringInstance(BaseInternalInstance):
    CLASS = StringClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = None

    def set_value(self, value):
        return set_value(self, value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, StringInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
