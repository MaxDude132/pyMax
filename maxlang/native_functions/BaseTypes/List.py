from ..main import (
    BaseInternalClass,
    BaseInternalMethod,
    BaseInternalInstance,
    is_instance,
    make_internal_token,
)
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class ListInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("items"), is_varargs=True)]

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments[0].values)


class ListPush(BaseInternalMethod):
    name = make_internal_token("push")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("items"), is_varargs=True)]

    @property
    def return_token(self):
        return ListClass.name

    def call(self, interpreter, arguments):
        new_list = self.instance._copy()
        # Support varargs - add all items
        for item in arguments[0].values:
            new_list.additions.append(item)
        return new_list


class ListPop(BaseInternalMethod):
    name = make_internal_token("pop")

    @property
    def return_token(self):
        from .Pair import PairClass

        return PairClass.name

    def call(self, interpreter, arguments):
        from .Pair import PairInstance

        total_len = self.instance._total_length()
        if total_len == 0:
            raise InternalError(f"No more items in {self.instance.class_name}.")

        # Get the last item
        last_item = self.instance._get_value(total_len - 1)

        # Create new list without last item by compacting all but the last
        new_list = ListInstance(interpreter)
        new_list.base_values = [
            self.instance._get_value(i) for i in range(total_len - 1)
        ]

        # Return Pair(new_list, popped_value)
        return PairInstance(interpreter).set_values(new_list, last_item)


class ListGet(BaseInternalMethod):
    name = make_internal_token("get")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [IntClass.name]

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        try:
            index = int(arguments[0].value)
            return self.instance._get_value(index)
        except (ValueError, IndexError, TypeError, AttributeError):
            raise InternalError(f"{arguments[0]} is not a valid index.")


class ListSet(BaseInternalMethod):
    """New method: set value at index, returns new list."""

    name = make_internal_token("set")

    @property
    def parameters(self):
        return [
            Parameter(make_internal_token("index")),
            Parameter(make_internal_token("value")),
        ]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [IntClass.name]

    @property
    def return_token(self):
        return ListClass.name

    def call(self, interpreter, arguments):
        try:
            index = int(arguments[0].value)
            value = arguments[1]

            # Validate index is in range
            if index < 0 or index >= self.instance._total_length():
                raise InternalError(f"Index {index} out of range")

            new_list = self.instance._copy()
            new_list.modifications[index] = value
            return new_list
        except (ValueError, TypeError, AttributeError):
            raise InternalError(f"{arguments[0]} is not a valid index.")


class ListExtend(BaseInternalMethod):
    name = make_internal_token("extend")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [ListClass.name]

    @property
    def return_token(self):
        return ListClass.name

    def call(self, interpreter, arguments):
        if not is_instance(interpreter, arguments[0], ListClass.name):
            raise InternalError(
                "Can only extend a List with another list. Use push to add an item to a List."
            )

        if arguments[0] == self.instance:
            raise InternalError("Cannot extend a List with itself.")

        new_list = self.instance._copy()
        new_list.extend(arguments[0].values)
        return new_list


class ListIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    @property
    def return_token(self):
        from ..Interators.ListIterator import ListIteratorClass

        return ListIteratorClass.name

    def call(self, interpreter, arguments):
        from ..Interators.ListIterator import ListIteratorInstance

        return ListIteratorInstance(interpreter).set_value(self.instance)


class ListAdd(BaseInternalMethod):
    name = make_internal_token("add")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [ListClass.name]

    def call(self, interpreter, arguments):
        if is_instance(interpreter, arguments[0], ListClass.name):
            new_list = ListInstance(interpreter).set_values(*self.instance.values)
            new_list.extend(arguments[0].values)
            return new_list

        raise InternalError(
            "Can only add a List to a List. Use the push method to add items to a List."
        )


class ListMultiply(BaseInternalMethod):
    name = make_internal_token("multiply")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return ListInstance(interpreter).set_values(
                *(self.instance.values * arguments[0].value)
            )

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class ListEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [ListClass.name]

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], ListClass.name):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class ListLength(BaseInternalMethod):
    name = make_internal_token("length")

    @property
    def return_token(self):
        from .Int import IntClass

        return IntClass.name

    def call(self, interpreter, arguments):
        from .Int import IntInstance

        return IntInstance(interpreter).set_value(self.instance._total_length())


class ListToBool(BaseInternalMethod):
    name = make_internal_token("toBool")

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.values) != 0)


class ListToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from .String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (
            self.instance.klass.interpreter.stringify(v, True)
            for v in self.instance.values
        )
        return StringInstance(interpreter).set_value(
            f"{self.instance.klass.name.lexeme}({', '.join(stringified)})"
        )


class ListClass(BaseInternalClass):
    name = make_internal_token("List")
    FIELDS = (
        ListInit,
        ListPush,
        ListGet,
        ListSet,
        ListPop,
        ListExtend,
        ListIterate,
        ListAdd,
        ListMultiply,
        ListEquals,
        ListLength,
        ListToBool,
        ListToString,
    )

    @property
    def instance_class(self):
        return ListInstance

    def upper_arity(self):
        return float("inf")


class ListInstance(BaseInternalInstance):
    CLASS = ListClass
    COMPACTION_THRESHOLD = 10

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.base_values = []  # Original immutable base
        self.modifications = {}  # {index: value} overrides
        self.additions = []  # Items appended after base
        self.parent = None  # Previous version reference
        self.depth = 0  # Chain depth for compaction
        self._ref_count = 0  # Track external references

    def set_values(self, *args):
        self.base_values = [*args]
        return self

    def _total_length(self):
        """Calculate total length including parent chain."""
        base_len = len(self.base_values)
        additions_len = len(self.additions)

        # Count items from parent if exists
        if self.parent:
            parent_len = self.parent._total_length()
            return max(parent_len, base_len) + additions_len

        return base_len + additions_len

    def _get_value(self, index):
        """Get value with modification chain lookup."""
        # Check additions first
        base_len = (
            len(self.base_values) if not self.parent else self.parent._total_length()
        )
        if index >= base_len:
            addition_index = index - base_len
            if addition_index < len(self.additions):
                return self.additions[addition_index]
            raise IndexError(f"Index {index} out of range")

        # Check modifications
        if index in self.modifications:
            value = self.modifications[index]
            if value is None:  # Marked as removed
                raise IndexError(f"Index {index} has been removed")
            return value

        # Check base values
        if index < len(self.base_values):
            return self.base_values[index]

        # Walk parent chain
        if self.parent:
            return self.parent._get_value(index)

        raise IndexError(f"Index {index} out of range")

    def _copy(self):
        """Create a new version for modifications."""
        new_instance = ListInstance(self.interpreter)
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
        # Collect all values into new base
        total_len = self._total_length()
        self.base_values = [self._get_value(i) for i in range(total_len)]
        self.modifications = {}
        self.additions = []
        self.parent = None
        self.depth = 0

    @property
    def values(self):
        """Property to maintain compatibility with existing code."""
        # Return all values as a list
        try:
            return [self._get_value(i) for i in range(self._total_length())]
        except IndexError:
            return []

    @values.setter
    def values(self, new_values):
        """Setter to maintain compatibility."""
        self.base_values = new_values
        self.modifications = {}
        self.additions = []
        self.parent = None
        self.depth = 0

    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.interpreter, [])

    def extend(self, other_list):
        self.additions.extend(other_list)

    def __eq__(self, other):
        if not isinstance(other, ListInstance):
            return False

        return self.values == other.values

    def __hash__(self):
        return hash(str(self))
