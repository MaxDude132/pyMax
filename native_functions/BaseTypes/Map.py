
from __future__ import annotations
from typing import Any

from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance
from .Pair import PairInstance, PairClass
from ..next import internal_next
from errors import InternalError


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
        pair_class = interpreter.globals.internal_get(PairClass.name)
        values = [PairInstance(pair_class, k, v) for k, v in self.instance.values.items()]
        return internal_next(interpreter, values)
    

class MapRemove(BaseInternalMethod):
    name = "remove"
    instance: MapInstance

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        pair_class = interpreter.globals.internal_get(PairClass.name)
        return PairInstance(pair_class, arguments[0], self.instance.values.pop(arguments[0]))
    

class MapAdd(BaseInternalMethod):
    name = "add"
    instance: MapInstance

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        new_map = MapInstance(self.instance.klass, *self.instance.get_pairs())
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
        if isinstance(arguments[0], MapInstance):
            return MapInstance(self.instance.klass, self.instance == arguments[0])

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class MapIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        klass = interpreter.environment.internal_get(BoolClass.name)
        return BoolInstance(klass, len(self.values) != 0)


class MapToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringClass, StringInstance

        klass = interpreter.environment.internal_get(StringClass.name)
        stringified = (" -> ".join((self.instance.klass.interpreter.stringify(k, True), self.instance.klass.interpreter.stringify(v, True))) for k, v in self.instance.values.items())
        return StringInstance(klass, f"{self.instance.klass.name}({", ".join(stringified)})")


class MapClass(BaseInternalClass):
    name = "Map"

    def upper_arity(self):
        return float("inf")
    
    def call(self, interpreter, arguments: list[tuple[Any, Any]]):
        return MapInstance(self, *arguments)
    

class MapInstance(BaseInternalInstance):
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
    
    def __init__(self, klass,  *args: PairInstance):
        super().__init__(klass)
        self.values = {arg.first: arg.second for arg in args}
    
    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.klass.interpreter, [])
    
    def __iter__(self):
        return iter(self.get_pairs())
    
    def get_pairs(self):
        pair_class = self.klass.interpreter.globals.internal_get(PairClass.name)

        pairs = []
        for k, v in self.values.items():
            pairs.append(PairInstance(pair_class, k, v))

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
