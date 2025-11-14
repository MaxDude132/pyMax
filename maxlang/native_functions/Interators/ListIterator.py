from __future__ import annotations

from ..main import BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from .BaseIterator import BaseIteratorClass, BaseIteratorInstance


class ListIteratorNext(BaseInternalMethod):
    instance: ListIteratorInstance
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

        # Get current value using _get_value method (List uses persistent structure)
        value = self.instance.value._get_value(self.instance.current)

        # Create new iterator with incremented position
        new_iterator = ListIteratorInstance(interpreter)
        new_iterator.value = self.instance.value
        new_iterator.limit = self.instance.limit
        new_iterator.current = self.instance.current + 1

        return PairInstance(interpreter).set_values(value, new_iterator)


class ListIteratorClass(BaseIteratorClass):
    name = make_internal_token("ListIterator")
    FIELDS = (ListIteratorNext,)

    @property
    def instance_class(self):
        return ListIteratorInstance


class ListIteratorInstance(BaseIteratorInstance):
    CLASS = ListIteratorClass

    def __init__(self, interpreter):
        from ..BaseTypes.List import ListClass

        super().__init__(interpreter)
        self.value: ListClass = None
        self.limit: int = None
        self.current = 0

    def set_value(self, value):
        from ..BaseTypes.List import ListClass

        if is_instance(self.interpreter, value, ListClass.name):
            self.value = value
            self.limit = self.value._total_length()
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self
