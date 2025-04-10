from __future__ import annotations

from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance, is_instance, make_internal_token
from .Pair import PairInstance, PairClass
from ..next import internal_next
from maxlang.errors import InternalError


class MapInit(BaseInternalMethod):
    name = make_internal_token("init")

    def lower_arity(self):
        return 0

    def upper_arity(self):
        return float("inf")

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments)


class MapPush(BaseInternalMethod):
    name = make_internal_token("push")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 2

    def call(self, interpreter, arguments):
        if is_instance(interpreter, arguments[0], PairClass.name):
            self.instance.values[arguments[0].first] = arguments[0].second
        else:
            self.instance.values[arguments[0]] = arguments[1]


class MapGet(BaseInternalMethod):
    name = make_internal_token("get")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        try:
            return self.instance.values[arguments[0]]
        except KeyError:
            raise InternalError(
                f"Could not find key {arguments[0]} in {MapClass.name}."
            )


class MapIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    def call(self, interpreter, arguments):
        values = [
            PairInstance(interpreter).set_values(k, v)
            for k, v in self.instance.values.items()
        ]
        return internal_next(interpreter, values)


class MapRemove(BaseInternalMethod):
    name = make_internal_token("remove")
    instance: MapInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        return PairInstance(interpreter).set_values(
            arguments[0], self.instance.values.pop(arguments[0])
        )


class MapAdd(BaseInternalMethod):
    name = make_internal_token("add")
    instance: MapInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        new_map = MapInstance(interpreter).set_values(*self.instance.get_pairs())
        if is_instance(interpreter, arguments[0], MapClass.name):
            new_map.update(arguments[0])
        elif is_instance(interpreter, arguments[0], PairClass.name):
            new_map.add_pair(arguments[0])
        else:
            raise InternalError("Can only add maps or pairs to maps.")

        return new_map


class MapEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], MapClass.name):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class MapIsTrue(BaseInternalMethod):
    name = make_internal_token("isTrue")

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.values) != 0)


class MapToString(BaseInternalMethod):
    name = make_internal_token("toString")

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (
            " -> ".join(
                (interpreter.stringify(k, True), interpreter.stringify(v, True))
            )
            for k, v in self.instance.values.items()
        )
        return StringInstance(interpreter).set_value(
            f"{self.instance.klass.name.lexeme}({", ".join(stringified)})"
        )


class MapClass(BaseInternalClass):
    name = make_internal_token("Map")
    FIELDS = (
        MapInit,
        MapPush,
        MapGet,
        MapRemove,
        MapIterate,
        MapAdd,
        MapEquals,
        MapIsTrue,
        MapToString,
    )

    @property
    def instance_class(self):
        return MapInstance

    def upper_arity(self):
        return float("inf")


class MapInstance(BaseInternalInstance):
    CLASS = MapClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.values = {}

    def set_values(self, *args: PairInstance):
        self.values = {arg.first: arg.second for arg in args}
        return self

    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.klass.interpreter, [])

    def __iter__(self):
        return iter(self.get_pairs())

    def get_pairs(self):
        pairs = []
        for k, v in self.values.items():
            pairs.append(PairInstance(self.interpreter).set_values(k, v))

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
