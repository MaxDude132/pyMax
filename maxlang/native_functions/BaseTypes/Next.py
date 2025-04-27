from __future__ import annotations

from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalAttribute, make_internal_token


class NextSentinel:
    def __str__(self):
        return "NEXT_SENTINEL"


NEXT_SENTINEL = NextSentinel()


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

    @property
    def instance_class(self):
        return NextInstance

    def call(self, interpreter, arguments):
        self.value = arguments[0]
        return self


class NextInstance(BaseInternalInstance):
    CLASS = NextClass
    FIELDS = (
        NextValue,
        NextIsEnd,
    )

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = NEXT_SENTINEL
        self.is_end = NEXT_SENTINEL

    def set_values(self, value, is_end):
        self.value = value
        self.is_end = is_end
        return self

    def __str__(self):
        return f"{self.class_name}({self.interpreter.stringify(self.value, True)}, {self.callback})"
