from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance, is_instance, make_internal_token
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class ObjectEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("other")
            )
        ]

    @property
    def return_token(self):
        from .Bool import BoolClass
        
        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], ObjectClass.name):
            return BoolInstance(interpreter).set_value(False)

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class ObjectIsTrue(BaseInternalMethod):
    name = make_internal_token("isTrue")

    @property
    def return_token(self):
        from .Bool import BoolClass
        
        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(False)


class ObjectToString(BaseInternalMethod):
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
            f"{self.instance.klass.name.lexeme}({", ".join(stringified)})"
        )


class ObjectClass(BaseInternalClass):
    name = make_internal_token("Object")
    FIELDS = (
        ObjectEquals,
        ObjectIsTrue,
        ObjectToString,
    )

    @property
    def instance_class(self):
        return ObjectInstance

    def upper_arity(self):
        return float("inf")


class ObjectInstance(BaseInternalInstance):
    CLASS = ObjectClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.values = []

    def __eq__(self, other):
        if not isinstance(other, ObjectInstance):
            return False

        return self.values == other.values

    def __hash__(self):
        return hash(str(self))
