from __future__ import annotations

from ..main import BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from .BaseIterator import BaseIteratorClass, BaseIteratorInstance


class IntIteratorNext(BaseInternalMethod):
    instance: IntIteratorInstance
    name = make_internal_token("next")

    @property
    def return_token(self):
        from ..BaseTypes.Int import IntClass

        return IntClass.name

    def call(self, interpreter, arguments):
        from ..BaseTypes.Pair import PairInstance

        # If we're past the end, return None (special marker for end-of-iteration)
        if self.instance.current >= self.instance.limit:
            return None

        # Get current value
        value = self.instance.current

        # Create new iterator with incremented position
        new_iterator = IntIteratorInstance(interpreter)
        new_iterator.limit = self.instance.limit
        new_iterator.current = self.instance.current + 1

        return PairInstance(interpreter).set_values(value, new_iterator)


class IntIteratorClass(BaseIteratorClass):
    name = make_internal_token("IntIterator")
    FIELDS = (IntIteratorNext,)

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
