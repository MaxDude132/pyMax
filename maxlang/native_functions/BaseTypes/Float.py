from ..main import (
    BaseInternalClass,
    BaseInternalInstance,
    BaseInternalMethod,
    is_instance,
    make_internal_token,
)
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class FloatInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [
            Parameter(
                make_internal_token("value"),
                methods_called=[make_internal_token("toFloat")],
            )
        ]

    def call(self, interpreter, arguments):
        self.instance.set_value(arguments[0])


class FloatAdd(BaseInternalMethod):
    name = make_internal_token("add")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [FloatClass.name, IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value + arguments[0].value
            )

        raise InternalError(
            f"Cannot add {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatSubstract(BaseInternalMethod):
    name = make_internal_token("substract")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [FloatClass.name, IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value - arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatMultiply(BaseInternalMethod):
    name = make_internal_token("multiply")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [FloatClass.name, IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value * arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatDivide(BaseInternalMethod):
    name = make_internal_token("divide")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [FloatClass.name, IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
            try:
                return FloatInstance(interpreter).set_value(
                    self.instance.value / arguments[0].value
                )
            except ZeroDivisionError:
                raise InternalError("Attempted division by zero.")

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [FloatClass.name, IntClass.name]

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], FloatClass.name, IntClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value == arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatGreaterThan(BaseInternalMethod):
    name = make_internal_token("greaterThan")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [FloatClass.name, IntClass.name]

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], FloatClass.name, IntClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value > arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatNegate(BaseInternalMethod):
    name = make_internal_token("negate")

    def call(self, interpreter, arguments):
        return FloatInstance(interpreter).set_value(-self.instance.value)


class FloatToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from .String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter).set_value(str(self.instance.value))


class FloatToInt(BaseInternalMethod):
    name = make_internal_token("toInt")

    @property
    def return_token(self):
        from .Int import IntClass

        return IntClass.name

    def call(self, interpreter, arguments):
        from .Int import IntInstance

        return IntInstance(interpreter).set_value(int(self.instance.value))


class FloatToBool(BaseInternalMethod):
    name = make_internal_token("toBool")

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(self.instance.value != 0.0)


class FloatClass(BaseInternalClass):
    name = make_internal_token("Float")
    FIELDS = (
        FloatInit,
        FloatAdd,
        FloatSubstract,
        FloatMultiply,
        FloatDivide,
        FloatEquals,
        FloatGreaterThan,
        FloatNegate,
        FloatToBool,
        FloatToString,
        FloatToInt,
    )

    @property
    def instance_class(self):
        return FloatInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1


class FloatInstance(BaseInternalInstance):
    CLASS = FloatClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = None

    def set_value(self, value):
        if isinstance(value, float):
            self.value = value
        elif isinstance(value, int):
            self.value = float(value)
        elif is_instance(self.interpreter, value, FloatClass.name):
            self.value = value.value
        elif hasattr(value, "internal_find_method"):
            to_float_method = value.internal_find_method("toFloat")
            bool_value = to_float_method.call(self.interpreter, [])
            if not is_instance(self.interpreter, bool_value, FloatClass.name):
                raise InternalError(
                    f"toFloat method did not return a Float for {value.class_name}."
                )
            self.value = bool_value.value
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not is_instance(self.interpreter, other, FloatClass.name):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
