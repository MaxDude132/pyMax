
from __future__ import annotations
from typing import Any

from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance
from .Pair import PairInstance
from ..next import internal_next
from maxlang.errors import InternalError


class MapPush(BaseInternalMethod):
    name = "push"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        if isinstance(arguments[0], PairInstance):
            self.instance.values[arguments[0].first] = arguments[0].second
        else:
            self.instance.values[arguments[0]] = arguments[1]

        return self.return_self()


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
            raise InternalError(f"Could not find key {arguments[0]} in {MapClass.name}.")
        

class MapIterate(BaseInternalMethod):
    name = "iterate"

    def call(self, interpreter, arguments):
        values = [PairInstance(interpreter, k, v) for k, v in self.instance.values.items()]
        return internal_next(interpreter, values)
    

class MapRemove(BaseInternalMethod):
    name = "remove"
    instance: MapInstance

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return PairInstance(interpreter, arguments[0], self.instance.values.pop(arguments[0]))
    

class MapAdd(BaseInternalMethod):
    name = "add"
    instance: MapInstance

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        new_map = MapInstance(interpreter, *self.instance.get_pairs())
        if isinstance(arguments[0], MapInstance):
            new_map.update(arguments[0])
        elif isinstance(arguments[0], PairInstance):
            new_map.add_pair(arguments[0])
        else:
            raise InternalError("Can only add maps or pairs to maps.")
        
        return new_map


class MapEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if isinstance(arguments[0], MapInstance):
            return BoolInstance(interpreter, self.instance == arguments[0])

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class MapIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter, len(self.values) != 0)


class MapToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (" -> ".join((interpreter.stringify(k, True), interpreter.stringify(v, True))) for k, v in self.instance.values.items())
        return StringInstance(interpreter, f"{self.instance.klass.name}({", ".join(stringified)})")


class MapClass(BaseInternalClass):
    name = "Map"

    def upper_arity(self):
        return float("inf")
    
    def call(self, interpreter, arguments: list[tuple[Any, Any]]):
        return MapInstance(interpreter, *arguments)
    

class MapInstance(BaseInternalInstance):
    CLASS = MapClass
    FIELDS = (
        MapPush,
        MapGet,
        MapRemove,
        MapIterate,
        MapAdd,
        MapEquals,
        MapIsTrue,
        MapToString,
    )
    
    def __init__(self, interpreter,  *args: PairInstance):
        super().__init__(interpreter)
        self.values = {arg.first: arg.second for arg in args}
    
    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.klass.interpreter, [])
    
    def __iter__(self):
        return iter(self.get_pairs())
    
    def get_pairs(self):
        pairs = []
        for k, v in self.values.items():
            pairs.append(PairInstance(self.interpreter, k, v))

        return pairs
    
    def update(self, other_map):
        for pair in other_map:
            self.add_pair(pair)

    def add_pair(self, pair):
        self.values[pair.first] = pair.second
    
    def __eq__(self, other):
        if not isinstance(other, MapInstance):
            return False
        
        return self.values == other.values
    
    def __hash__(self):
        return hash(str(self))
