from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance, is_instance, make_internal_token
from maxlang.errors import InternalError


class VoidEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], VoidClass.name):
            return BoolInstance(interpreter).set_value(False)

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class VoidIsTrue(BaseInternalMethod):
    name = make_internal_token("isTrue")

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(False)


class VoidToString(BaseInternalMethod):
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


class VoidClass(BaseInternalClass):
    name = make_internal_token("Void")
    FIELDS = (
        VoidEquals,
        VoidIsTrue,
        VoidToString,
    )

    @property
    def instance_class(self):
        return VoidInstance

    def upper_arity(self):
        return float("inf")


class VoidInstance(BaseInternalInstance):
    CLASS = VoidClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.values = []

    def __eq__(self, other):
        if not isinstance(other, VoidInstance):
            return False

        return self.values == other.values

    def __hash__(self):
        return hash(str(self))
