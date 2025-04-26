from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance, is_instance, make_internal_token
from ..next import internal_next
from maxlang.errors import InternalError


class VarArgsGet(BaseInternalMethod):
    name = make_internal_token("get")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        try:
            return self.instance.values[int(arguments[0].value)]
        except (ValueError, IndexError, TypeError, AttributeError):
            raise InternalError(
                f"{arguments[0]} is not a valid index."
            )


class VarArgsIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    def call(self, interpreter, arguments):
        return internal_next(interpreter, self.instance.values)


class VarArgsEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], VarArgsClass.name):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class VarArgsIsTrue(BaseInternalMethod):
    name = make_internal_token("isTrue")

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.values) != 0)


class VarArgsToString(BaseInternalMethod):
    name = make_internal_token("toString")

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (
            self.instance.klass.interpreter.stringify(v, True)
            for v in self.instance.values
        )
        return StringInstance(interpreter).set_value(
            f"{self.instance.klass.name.lexeme}({", ".join(stringified)})"
        )


class VarArgsClass(BaseInternalClass):
    name = make_internal_token("VarArgs")
    FIELDS = (
        VarArgsGet,
        VarArgsIterate,
        VarArgsEquals,
        VarArgsIsTrue,
        VarArgsToString,
    )

    @property
    def instance_class(self):
        return VarArgsInstance

    def upper_arity(self):
        return float("inf")


class VarArgsInstance(BaseInternalInstance):
    CLASS = VarArgsClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.values = []

    def set_values(self, *args):
        self.values = [*args]
        return self

    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.interpreter, [])

    def extend(self, other_list):
        self.values.extend(other_list)

    def __eq__(self, other):
        if not isinstance(other, VarArgsInstance):
            return False

        return self.values == other.values

    def __hash__(self):
        return hash(str(self))
