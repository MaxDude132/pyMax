from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, is_instance
from maxlang.errors import InternalError


class FloatInit(BaseInternalMethod):
    name = "init"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        self.instance.set_value(arguments[0])


class FloatAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

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
    name = "substract"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value - arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value * arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatDivide(BaseInternalMethod):
    name = "divide"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

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
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], FloatClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value == arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatGreaterThan(BaseInternalMethod):
    name = "greaterThan"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], FloatClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value > arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class FloatNegate(BaseInternalMethod):
    name = "negate"

    def call(self, interpreter, arguments):
        return FloatInstance(interpreter).set_value(-self.instance.value)


class FloatToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter).set_value(str(self.instance.value))


class FloatIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(self.instance.value != 0.0)


class FloatClass(BaseInternalClass):
    name = "Float"
    FIELDS = (
        FloatInit,
        FloatAdd,
        FloatSubstract,
        FloatMultiply,
        FloatDivide,
        FloatEquals,
        FloatGreaterThan,
        FloatNegate,
        FloatIsTrue,
        FloatToString,
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
        self.value = value
        return self

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not is_instance(self.interpreter, other, FloatInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
