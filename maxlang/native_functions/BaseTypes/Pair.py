from ..main import (
    BaseInternalClass,
    BaseInternalAttribute,
    BaseInternalInstance,
    BaseInternalMethod,
    make_internal_token,
)
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class PairInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [
            Parameter(make_internal_token("left")),
            Parameter(make_internal_token("right")),
        ]

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments)


class PairFirst(BaseInternalAttribute):
    name = make_internal_token("first")

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        return self.instance.first


class PairSecond(BaseInternalAttribute):
    name = make_internal_token("second")

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        return self.instance.second


class PairEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def return_type(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if isinstance(arguments[0], PairInstance):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class PairToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_type(self):
        from .String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = f"{self.instance.klass.name.lexeme}({interpreter.stringify(self.instance.first, True)}, {interpreter.stringify(self.instance.second, True)})"
        return StringInstance(interpreter).set_value(stringified)


class PairClass(BaseInternalClass):
    name = make_internal_token("Pair")
    FIELDS = (PairInit, PairFirst, PairSecond, PairEquals, PairToString)

    @property
    def instance_class(self):
        return PairInstance


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
