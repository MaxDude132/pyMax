from typing import Any

from .main import BaseInternalClass, BaseInternalMethod


class MapAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 2
    
    def upper_arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        self.instance.values[arguments[0]] = arguments[1]


class MapGet(BaseInternalMethod):
    name = "get"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return self.instance.values[arguments[0]]


class Map(BaseInternalClass):
    name = "map"

    METHODS = (
        MapAdd,
        MapGet,
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
