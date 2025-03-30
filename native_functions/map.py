
from __future__ import annotations
from typing import Any

from .main import BaseInternalClass, BaseInternalMethod
from .pair import Pair
from .next import internal_next
from errors import InternalError


class MapAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        if isinstance(arguments[0], Pair):
            self.instance.values[arguments[0].first] = arguments[0].second
        else:
            self.instance.values[arguments[0]] = arguments[1]


class MapGet(BaseInternalMethod):
    name = "get"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            return self.instance.values[arguments[0]]
        except KeyError:
            raise InternalError(f"Could not find key {arguments[0]} in map.")
        

class MapIterate(BaseInternalMethod):
    name = "iterate"

    def call(self, interpreter, arguments):
        values = [Pair(interpreter).call(interpreter, [k, v]) for k, v in self.instance.values.items()]
        return internal_next(interpreter, values)
    

class MapRemove(BaseInternalMethod):
    name = "remove"
    instance: Map

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        pair = Pair(interpreter).call(interpreter, [arguments[0], self.instance.values.pop(arguments[0])])
        return pair


class Map(BaseInternalClass):
    name = "map"

    FIELDS = (
        MapAdd,
        MapGet,
        MapRemove,
        MapIterate,
    )

    def init(self):
        self.values = {}

    def upper_arity(self):
        return float("inf")
    
    def call(self, interpreter, arguments: list[tuple[Any, Any]]):
        for arg in arguments:
            self.values[arg[0]] = arg[1]
        return self
    
    def __str__(self) -> str:
        stringified = (" -> ".join((self.interpreter.stringify(k, True), self.interpreter.stringify(v, True))) for k, v in self.values.items())
        return f"map({", ".join(stringified)})"
