from __future__ import annotations
from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, is_instance
from maxlang.errors import InternalError


def set_value(instance: BoolInstance, value: bool):
    if isinstance(value, bool):
        instance.value = value
    else:
        try:
            instance.value = (
                value.internal_find_method("isTrue")
                .call(instance.interpreter, [])
                .value
            )
        except KeyError:
            raise InternalError(
                f"class {value.class_name} does not implement the isTrue method."
            )
    return instance


class BoolInit(BaseInternalMethod):
    name = "init"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        set_value(self.instance, arguments[0])


class BoolEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if is_instance(interpreter, arguments[0], BoolClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value is arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class BoolIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        return BoolInstance(interpreter).set_value(self.instance.value)


class BoolToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter).set_value(
            "true" if self.instance.value else "false"
        )


class BoolClass(BaseInternalClass):
    name = "Bool"
    FIELDS = (
        BoolInit,
        BoolEquals,
        BoolIsTrue,
        BoolToString,
    )

    @property
    def instance_class(self):
        return BoolInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1


class BoolInstance(BaseInternalInstance):
    CLASS = BoolClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = None

    def set_value(self, value: bool):
        return set_value(self, value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, BoolInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
