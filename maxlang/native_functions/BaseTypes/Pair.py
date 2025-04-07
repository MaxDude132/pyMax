from ..main import (
    BaseInternalClass,
    BaseInternalAttribute,
    BaseInternalInstance,
    BaseInternalMethod,
)
from maxlang.errors import InternalError


class PairInit(BaseInternalMethod):
    name = "init"

    def lower_arity(self):
        return 2

    def upper_arity(self):
        return 2

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments)


class PairFirst(BaseInternalAttribute):
    name = "first"

    def call(self, interpreter, arguments):
        return self.instance.first


class PairSecond(BaseInternalAttribute):
    name = "second"

    def call(self, interpreter, arguments):
        return self.instance.second


class PairEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if isinstance(arguments[0], PairInstance):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class PairToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = f"{self.instance.class_name}({interpreter.stringify(self.instance.first, True)}, {interpreter.stringify(self.instance.second, True)})"
        return StringInstance(interpreter).set_value(
            f"{self.class_name}({stringified})"
        )


class PairClass(BaseInternalClass):
    name = "Pair"
    FIELDS = (PairInit, PairFirst, PairSecond, PairEquals, PairToString)

    @property
    def instance_class(self):
        return PairInstance

    def lower_arity(self):
        return 2

    def upper_arity(self):
        return 2


class PairInstance(BaseInternalInstance):
    CLASS = PairClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.first = None
        self.second = None

    def set_values(self, first, second):
        self.first = first
        self.second = second
        return self

    def __str__(self):
        return self.internal_find_method("toString").call(self.klass.interpreter, [])

    def __eq__(self, other):
        if not isinstance(other, PairInstance):
            return False

        return self.first == other.first and self.second == other.second

    def __hash__(self):
        return hash(str(self))
