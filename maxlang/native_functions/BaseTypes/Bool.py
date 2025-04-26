from __future__ import annotations
from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class BoolInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("value")
            )
        ]

    def call(self, interpreter, arguments):
        self.instance.set_value(arguments[0])


class BoolEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("other")
            )
        ]

    def call(self, interpreter, arguments):
        if is_instance(interpreter, arguments[0], BoolClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value is arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class BoolIsTrue(BaseInternalMethod):
    name = make_internal_token("isTrue")

    def call(self, interpreter, arguments):
        return BoolInstance(interpreter).set_value(self.instance.value)


class BoolToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from .String import StringClass
        
        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter).set_value(
            "true" if self.instance.value else "false"
        )


class BoolClass(BaseInternalClass):
    name = make_internal_token("Bool")
    FIELDS = (
        BoolInit,
        BoolEquals,
        BoolIsTrue,
        BoolToString,
    )

    @property
    def instance_class(self):
        return BoolInstance


class BoolInstance(BaseInternalInstance):
    CLASS = BoolClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = None

    def set_value(self, value: bool):
        if isinstance(value, bool):
            self.value = value
        elif is_instance(self.interpreter, value, BoolClass.name):
            self.value = value.value
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")
        
        return self

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, BoolInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
