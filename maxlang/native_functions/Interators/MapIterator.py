from __future__ import annotations

from ..main import BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from .BaseIterator import BaseIteratorClass, BaseIteratorInstance
from ..BaseTypes.Next import NextInstance


class MapIteratorNext(BaseInternalMethod):
    instance: MapIteratorInstance
    name = make_internal_token("next")

    @property
    def return_token(self):
        from ..BaseTypes.Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        value = self.instance.pairs[self.instance.current]
        next_ = NextInstance(interpreter).set_values(value, self.instance.current == self.instance.limit - 1)
        self.instance.current += 1
        return next_


class MapIteratorClass(BaseIteratorClass):
    name = make_internal_token("MapIterator")
    FIELDS = (
        MapIteratorNext,
    )

    @property
    def instance_class(self):
        return MapIteratorInstance


class MapIteratorInstance(BaseIteratorInstance):
    CLASS = MapIteratorClass

    def __init__(self, interpreter):
        from ..BaseTypes.Map import MapClass
        from ..BaseTypes.Pair import PairClass

        super().__init__(interpreter)
        self.value: MapClass = None
        self.pairs: list[PairClass]
        self.limit: int = None
        self.current = 0

    def set_value(self, value):
        from ..BaseTypes.Map import MapClass

        if is_instance(self.interpreter, value, MapClass.name):
            self.value = value
            self.pairs = self.value.get_pairs()
            self.limit = len(self.value.values)
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self
