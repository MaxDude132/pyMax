from __future__ import annotations

from ..main import BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from .BaseIterator import BaseIteratorClass, BaseIteratorInstance


class VarArgsIteratorNext(BaseInternalMethod):
    instance: VarArgsIteratorInstance
    name = make_internal_token("next")

    @property
    def return_token(self):
        from ..BaseTypes.Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        from ..BaseTypes.Pair import PairInstance

        # If we're past the end, return None (special marker for end-of-iteration)
        if self.instance.current >= self.instance.limit:
            return None

        # Get current value
        value = self.instance.value.values[self.instance.current]

        # Create new iterator with incremented position
        new_iterator = VarArgsIteratorInstance(interpreter)
        new_iterator.value = self.instance.value
        new_iterator.limit = self.instance.limit
        new_iterator.current = self.instance.current + 1

        return PairInstance(interpreter).set_values(value, new_iterator)


class VarArgsIteratorClass(BaseIteratorClass):
    name = make_internal_token("VarArgsIterator")
    FIELDS = (VarArgsIteratorNext,)

    @property
    def instance_class(self):
        return VarArgsIteratorInstance


class VarArgsIteratorInstance(BaseIteratorInstance):
    CLASS = VarArgsIteratorClass

    def __init__(self, interpreter):
        from ..BaseTypes.VarArgs import VarArgsClass

        super().__init__(interpreter)
        self.value: VarArgsClass = None
        self.limit: int = None
        self.current = 0

    def set_value(self, value):
        from ..BaseTypes.VarArgs import VarArgsClass

        if is_instance(self.interpreter, value, VarArgsClass.name):
            self.value = value
            self.limit = len(self.value.values)
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self
