from __future__ import annotations

from ..main import (
    BaseInternalClass,
    BaseInternalInstance,
    BaseInternalAttribute,
    make_internal_token,
    BaseInternalMethod,
)
from maxlang.parse.expressions import Parameter


class NextInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [
            Parameter(make_internal_token("value")),
            Parameter(make_internal_token("is_end")),
        ]

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments)


class NextValue(BaseInternalAttribute):
    name = make_internal_token("value")
    instance: NextInstance

    def call(self, interpreter, arguments):
        return self.instance.value


class NextIsEnd(BaseInternalAttribute):
    name = make_internal_token("is_end")
    instance: NextInstance

    def call(self, interpreter, arguments):
        return self.instance.is_end


class NextClass(BaseInternalClass):
    name = make_internal_token("Next")
    FIELDS = (
        NextInit,
        NextValue,
        NextIsEnd,
    )

    @property
    def instance_class(self):
        return NextInstance


class NextInstance(BaseInternalInstance):
    CLASS = NextClass

    def __init__(self, interpreter):
        from ..BaseTypes.Bool import BoolInstance

        super().__init__(interpreter)
        self.value = None
        self.is_end: BoolInstance = None

    def set_values(self, value, is_end):
        self.value = value
        self.is_end = is_end
        return self

    def __str__(self):
        return f"{self.class_name}({self.interpreter.stringify(self.value, True)}, {self.callback})"

    def __bool__(self):
        return self.is_end.value
