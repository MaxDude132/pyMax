from __future__ import annotations

from ..main import BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from .BaseIterator import BaseIteratorClass, BaseIteratorInstance
from ..BaseTypes.Next import NextInstance


class IntIteratorNext(BaseInternalMethod):
    instance: IntIteratorInstance
    name = make_internal_token("next")

    @property
    def return_token(self):
        from ..BaseTypes.Int import IntClass

        return IntClass.name

    def call(self, interpreter, arguments):
        from ..BaseTypes.Bool import BoolInstance

        value = self.instance.current
        is_end = BoolInstance(interpreter).set_value(value == self.instance.limit - 1)
        next_ = NextInstance(interpreter).set_values(value, is_end)
        self.instance.current += 1
        return next_


class IntIteratorClass(BaseIteratorClass):
    name = make_internal_token("IntIterator")
    FIELDS = (
        IntIteratorNext,
    )

    @property
    def instance_class(self):
        return IntIteratorInstance


class IntIteratorInstance(BaseIteratorInstance):
    CLASS = IntIteratorClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.limit: int = None
        self.current = 0

    def set_value(self, value):
        from ..BaseTypes.Int import IntClass

        if is_instance(self.interpreter, value, IntClass.name):
            self.limit = value.value
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self
