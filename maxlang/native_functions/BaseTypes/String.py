from __future__ import annotations

from ..main import (
    BaseInternalClass,
    BaseInternalInstance,
    BaseInternalMethod,
    is_instance,
    make_internal_token,
)
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


def set_value(instance: StringInstance, value: str):
    instance.value = value
    return instance


class StringInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("value"),
                methods_called=[make_internal_token("toString")],
            )
        ]

    def call(self, interpreter, arguments):
        set_value(self.instance, arguments[0])


class StringAdd(BaseInternalMethod):
    name = make_internal_token("add")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("value"),
                methods_called=[make_internal_token("toString")],
            )
        ]

    def call(self, interpreter, arguments):
        to_string_method = arguments[0].internal_find_method("toString")
        string_value = to_string_method.call(interpreter, [])
        if not is_instance(interpreter, string_value, StringClass.name):
            raise InternalError(
                f"toString method did not return a String for {arguments[0].class_name}."
            )

        return StringInstance(interpreter).set_value(
            self.instance.value + string_value.value
        )


class StringMultiply(BaseInternalMethod):
    name = make_internal_token("multiply")

    @property
    def parameters(self):
        from .Int import IntClass

        return [Parameter([IntClass.name], make_internal_token("value"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return StringInstance(interpreter).set_value(
                self.instance.value * arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class StringEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [Parameter([self.instance.klass.name], make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [StringClass.name]

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], StringClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value == arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class StringIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    @property
    def return_token(self):
        from ..Interators.StringIterator import StringIteratorClass

        return StringIteratorClass.name

    def call(self, interpreter, arguments):
        from ..Interators.StringIterator import StringIteratorInstance

        return StringIteratorInstance(interpreter).set_value(self.instance)


class StringToBool(BaseInternalMethod):
    name = make_internal_token("toBool")

    @property
    def return_token(self):
        from .String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.value) != 0)


class StringToString(BaseInternalMethod):
    name = make_internal_token("toString")

    def call(self, interpreter, arguments):
        return StringInstance(interpreter).set_value(self.instance.value)


class StringToInt(BaseInternalMethod):
    name = make_internal_token("toInt")

    @property
    def return_token(self):
        from .Int import IntClass

        return IntClass.name

    def call(self, interpreter, arguments):
        from .Int import IntInstance, IntClass

        try:
            return IntInstance(interpreter).set_value(int(self.instance.value))
        except ValueError:
            pass

        try:
            return IntInstance(interpreter).set_value(int(float(self.instance.value)))
        except ValueError:
            pass

        raise InternalError(
            f"Cannot convert value {self.instance.value} to <{IntClass.name.lexeme}>"
        )


class StringToFloat(BaseInternalMethod):
    name = make_internal_token("toFloat")

    @property
    def return_token(self):
        from .Float import FloatClass

        return FloatClass.name

    def call(self, interpreter, arguments):
        from .Float import FloatInstance, FloatClass

        try:
            return FloatInstance(interpreter).set_value(float(self.instance.value))
        except ValueError:
            raise InternalError(
                f"Cannot convert value {self.instance.value} to <{FloatClass.name.lexeme}>"
            )


class StringClass(BaseInternalClass):
    name = make_internal_token("String")
    FIELDS = (
        StringInit,
        StringAdd,
        StringMultiply,
        StringEquals,
        StringToBool,
        StringIterate,
        StringToString,
        StringToInt,
        StringToFloat,
    )

    @property
    def instance_class(self):
        return StringInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        return StringInstance(interpreter).set_value(arguments[0])


class StringInstance(BaseInternalInstance):
    CLASS = StringClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = None

    def set_value(self, value):
        value = self.interpreter.stringify(value)
        return set_value(self, value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, StringInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
