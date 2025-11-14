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
        return [Parameter(make_internal_token("items"), is_varargs=True)]

    @property
    def allowed_types(self):
        return [PairClass.name]

    @property
    def return_token(self):
        return MapClass.name

    def call(self, interpreter, arguments):
        new_map = self.instance._copy()

        # Support varargs - add all pairs
        for item in arguments[0].values:
            if is_instance(interpreter, item, PairClass.name):
                new_map.modifications[item.first] = item.second
                if item.first in new_map.removals:
                    new_map.removals.remove(item.first)
            else:
                raise InternalError(
                    f"Invalid value passed to {self.instance.class_name}."
                )

        return new_map


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
            return self.instance._get_value(arguments[0])
        except KeyError:
            raise InternalError(
                f"Could not find key {arguments[0]} in {self.instance.class_name}."
            )


class MapSet(BaseInternalMethod):
    """New method: set key-value, returns new map."""

    name = make_internal_token("set")

    @property
    def parameters(self):
        return [
            Parameter(make_internal_token("key")),
            Parameter(make_internal_token("value")),
        ]

    @property
    def return_token(self):
        return MapClass.name

    def call(self, interpreter, arguments):
        key = arguments[0]
        value = arguments[1]

        new_map = self.instance._copy()
        new_map.modifications[key] = value
        if key in new_map.removals:
            new_map.removals.remove(key)

        return new_map


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
        return PairClass.name

    def call(self, interpreter, arguments):
        try:
            # Get the value before removing
            value = self.instance._get_value(arguments[0])

            # Create new map without this key
            new_map = self.instance._copy()
            new_map.removals.add(arguments[0])

            # Return Pair(new_map, removed_value)
            return PairInstance(interpreter).set_values(new_map, value)
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


class MapLength(BaseInternalMethod):
    name = make_internal_token("length")

    @property
    def return_token(self):
        from .Int import IntClass

        return IntClass.name

    def call(self, interpreter, arguments):
        from .Int import IntInstance

        return IntInstance(interpreter).set_value(len(self.instance._all_keys()))


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
        MapSet,
        MapRemove,
        MapIterate,
        MapAdd,
        MapEquals,
        MapLength,
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
    COMPACTION_THRESHOLD = 10

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.base_values = {}  # Original immutable base
        self.modifications = {}  # {key: value} overrides/additions
        self.removals = set()  # Keys marked for removal
        self.parent = None  # Previous version reference
        self.depth = 0  # Chain depth for compaction
        self._ref_count = 0  # Track external references

    def set_values(self, args: VarArgsInstance):
        for arg in args.values:
            if not is_instance(self.interpreter, arg, PairClass.name):
                raise InternalError(f"Invalid value passed to {self.class_name}.")
            self.base_values[arg.first] = arg.second

        return self

    def _get_value(self, key):
        """Get value with modification chain lookup."""
        # Check if removed
        if key in self.removals:
            raise KeyError(key)

        # Check modifications
        if key in self.modifications:
            return self.modifications[key]

        # Check base
        if key in self.base_values:
            return self.base_values[key]

        # Walk parent chain
        if self.parent:
            return self.parent._get_value(key)

        raise KeyError(key)

    def _has_key(self, key):
        """Check if key exists in chain."""
        if key in self.removals:
            return False
        if key in self.modifications or key in self.base_values:
            return True
        if self.parent:
            return self.parent._has_key(key)
        return False

    def _all_keys(self):
        """Get all keys from chain."""
        keys = set()

        # Collect from base
        keys.update(self.base_values.keys())

        # Collect from modifications
        keys.update(self.modifications.keys())

        # Collect from parent
        if self.parent:
            keys.update(self.parent._all_keys())

        # Remove deleted keys
        keys -= self.removals

        return keys

    def _copy(self):
        """Create a new version for modifications."""
        new_instance = MapInstance(self.interpreter)
        new_instance.parent = self
        new_instance.depth = self.depth + 1

        # Auto-compact if chain is deep AND old instances are unreferenced
        if new_instance.depth > self.COMPACTION_THRESHOLD:
            if self._should_compact():
                new_instance._compact()

        return new_instance

    def _should_compact(self):
        """Check if we should compact the chain.

        Compaction should occur if:
        1. Depth exceeds threshold
        2. There are no external references to intermediate nodes (Python's GC handles this)

        Since Python uses reference counting, unreferenced objects will be GC'd automatically.
        We just need to check if compaction makes sense based on depth.
        """
        # For now, always compact when threshold is exceeded
        # Python's GC will clean up unreferenced intermediate nodes
        return True

    def _compact(self):
        """Flatten the modification chain."""
        # Collect all key-value pairs into new base
        all_keys = self._all_keys()
        self.base_values = {key: self._get_value(key) for key in all_keys}
        self.modifications = {}
        self.removals = set()
        self.parent = None
        self.depth = 0

    @property
    def values(self):
        """Property to maintain compatibility with existing code."""
        result = {}
        for key in self._all_keys():
            try:
                result[key] = self._get_value(key)
            except KeyError:
                pass
        return result

    @values.setter
    def values(self, new_values):
        """Setter to maintain compatibility."""
        self.base_values = new_values
        self.modifications = {}
        self.removals = set()
        self.parent = None
        self.depth = 0

    def __str__(self) -> str:
        return (
            self.internal_find_method("toString").call(self.klass.interpreter, []).value
        )

    def __iter__(self):
        return iter(self.get_pairs())

    def get_pairs(self):
        pairs = []
        for key in self._all_keys():
            try:
                value = self._get_value(key)
                pairs.append(PairInstance(self.interpreter).set_values(key, value))
            except KeyError:
                pass
        return pairs

    def update(self, other_map):
        for pair in other_map:
            self.add_pair(pair)

    def add_pair(self, pair):
        self.modifications[pair.first] = pair.second
        if pair.first in self.removals:
            self.removals.remove(pair.first)

    def __eq__(self, other):
        if not isinstance(other, MapInstance):
            return False

        return self.values == other.values

    def __hash__(self):
        return hash(id(self))
