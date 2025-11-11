from __future__ import annotations

from ..main import (
    BaseInternalClass,
    BaseInternalMethod,
    BaseInternalInstance,
    is_instance,
    make_internal_token,
)
from .Pair import PairInstance, PairClass
from .VarArgs import VarArgsInstance
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class MapInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("items"), is_varargs=True)]

    @property
    def allowed_types(self):
        return [PairClass.name]

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments)


class MapPush(BaseInternalMethod):
    name = make_internal_token("push")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("item"))]

    @property
    def allowed_types(self):
        return [PairClass.name]

    def call(self, interpreter, arguments):
        try:
            if is_instance(interpreter, arguments[0], PairClass.name):
                self.instance.values[arguments[0].first] = arguments[0].second
            else:
                self.instance.values[arguments[0]] = arguments[1]
        except (AttributeError, IndexError):
            raise InternalError(f"Invalid value passed to {self.class_name}.")


class MapGet(BaseInternalMethod):
    name = make_internal_token("get")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("key"))]

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        try:
            return self.instance.values[arguments[0]]
        except KeyError:
            raise InternalError(
                f"Could not find key {arguments[0]} in {self.instance.class_name}."
            )


class MapIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    @property
    def return_token(self):
        from ..Interators.MapIterator import MapIteratorClass

        return MapIteratorClass.name

    def call(self, interpreter, arguments):
        from ..Interators.MapIterator import MapIteratorInstance

        return MapIteratorInstance(interpreter).set_value(self.instance)


class MapRemove(BaseInternalMethod):
    name = make_internal_token("remove")
    instance: MapInstance

    @property
    def parameters(self):
        return [Parameter(make_internal_token("key"))]

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        try:
            return PairInstance(interpreter).set_values(
                arguments[0], self.instance.values.pop(arguments[0])
            )
        except KeyError:
            raise InternalError(
                f"Could not find key {arguments[0]} in {self.instance.class_name}."
            )


class MapAdd(BaseInternalMethod):
    name = make_internal_token("add")
    instance: MapInstance

    @property
    def parameters(self):
        return [Parameter(make_internal_token("key"))]

    @property
    def allowed_types(self):
        return [MapClass.name, PairClass.name]

    def call(self, interpreter, arguments):
        new_map = MapInstance(interpreter).set_values(
            VarArgsInstance(interpreter).set_values(*self.instance.get_pairs())
        )
        if is_instance(interpreter, arguments[0], MapClass.name):
            new_map.update(arguments[0])
        elif is_instance(interpreter, arguments[0], PairClass.name):
            new_map.add_pair(arguments[0])
        else:
            raise InternalError("Can only add maps or pairs to maps.")

        return new_map


class MapEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [MapClass.name]

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], MapClass.name):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class MapToBool(BaseInternalMethod):
    name = make_internal_token("toBool")

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.values) != 0)


class MapToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from .String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (
            " -> ".join(
                (interpreter.stringify(k, True), interpreter.stringify(v, True))
            )
            for k, v in self.instance.values.items()
        )
        return StringInstance(interpreter).set_value(
            f"{self.instance.klass.name.lexeme}({', '.join(stringified)})"
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
        MapToBool,
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

    def set_values(self, args: VarArgsInstance):
        for arg in args.values:
            if not is_instance(self.interpreter, arg, PairClass.name):
                raise InternalError(f"Invalid value passed to {self.class_name}.")
            self.values[arg.first] = arg.second

        return self

    def __str__(self) -> str:
        return (
            self.internal_find_method("toString").call(self.klass.interpreter, []).value
        )

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
        return hash(id(self))
