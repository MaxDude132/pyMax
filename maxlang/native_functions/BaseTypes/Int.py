from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, is_instance
from maxlang.errors import InternalError


class IntInit(BaseInternalMethod):
    name = "init"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        self.instance.set_value(arguments[0])


class IntAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance, FloatClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return IntInstance(interpreter).set_value(
                self.instance.value + arguments[0].value
            )
        if is_instance(interpreter, arguments[0], FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value + arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntSubstract(BaseInternalMethod):
    name = "substract"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance, FloatClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return IntInstance(interpreter).set_value(
                self.instance.value - arguments[0].value
            )
        if is_instance(interpreter, arguments[0], FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value - arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance, FloatClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return IntInstance(interpreter).set_value(
                self.instance.value * arguments[0].value
            )
        if is_instance(interpreter, arguments[0], FloatClass.name):
            return FloatInstance(interpreter).set_value(
                self.instance.value * arguments[0].value
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntDivide(BaseInternalMethod):
    name = "divide"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance, FloatClass

        try:
            if is_instance(interpreter, arguments[0], IntClass.name):
                return IntInstance(interpreter).set_value(
                    self.instance.value / arguments[0].value
                )
            if is_instance(interpreter, arguments[0], FloatClass.name):
                return FloatInstance(interpreter).set_value(
                    self.instance.value / arguments[0].value
                )
        except ZeroDivisionError:
            raise InternalError("Attempted division by zero.")

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], IntClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value == arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntGreaterThan(BaseInternalMethod):
    name = "greaterThan"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], IntClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value > arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntNegate(BaseInternalMethod):
    name = "negate"

    def call(self, interpreter, arguments):
        return IntInstance(interpreter).set_value(-self.instance.value)


class IntIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(self.instance.value != 0)


class IntToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter).set_value(str(self.instance.value))


class IntClass(BaseInternalClass):
    name = "Int"
    FIELDS = (
        IntInit,
        IntAdd,
        IntSubstract,
        IntMultiply,
        IntDivide,
        IntEquals,
        IntGreaterThan,
        IntNegate,
        IntIsTrue,
        IntToString,
    )

    @property
    def instance_class(self):
        return IntInstance

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1


class IntInstance(BaseInternalInstance):
    CLASS = IntClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.value = None

    def set_value(self, value):
        self.value = value
        return self

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, IntInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
