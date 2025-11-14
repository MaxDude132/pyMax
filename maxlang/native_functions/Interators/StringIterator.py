from __future__ import annotations

from ..main import BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from .BaseIterator import BaseIteratorClass, BaseIteratorInstance


class StringIteratorNext(BaseInternalMethod):
    instance: StringIteratorInstance
    name = make_internal_token("next")

    @property
    def return_token(self):
        from ..BaseTypes.String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from ..BaseTypes.Pair import PairInstance

        # If we're past the end, return None (special marker for end-of-iteration)
        if self.instance.current >= self.instance.limit:
            return None

        # Get current value
        value = self.instance.value.value[self.instance.current]

        # Create new iterator with incremented position
        new_iterator = StringIteratorInstance(interpreter)
        new_iterator.value = self.instance.value
        new_iterator.limit = self.instance.limit
        new_iterator.current = self.instance.current + 1

        return PairInstance(interpreter).set_values(value, new_iterator)


class StringIteratorClass(BaseIteratorClass):
    name = make_internal_token("StringIterator")
    FIELDS = (StringIteratorNext,)

    @property
    def instance_class(self):
        return StringIteratorInstance


class StringIteratorInstance(BaseIteratorInstance):
    CLASS = StringIteratorClass

    def __init__(self, interpreter):
        from ..BaseTypes.String import StringClass

        super().__init__(interpreter)
        self.value: StringClass = None
        self.limit: int = None
        self.current = 0

    def set_value(self, value):
        from ..BaseTypes.String import StringClass

        if is_instance(self.interpreter, value, StringClass.name):
            self.value = value
            self.limit = len(self.value.value)
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self
