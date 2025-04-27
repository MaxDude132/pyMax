from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, is_instance, make_internal_token
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter
from .Next import internal_next


class IntInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("value")
            )
        ]

    def call(self, interpreter, arguments):
        self.instance.set_value(arguments[0])


class IntAdd(BaseInternalMethod):
    name = make_internal_token("add")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("other")
            )
        ]

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
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntSubstract(BaseInternalMethod):
    name = make_internal_token("substract")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("other")
            )
        ]

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
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntMultiply(BaseInternalMethod):
    name = make_internal_token("multiply")

    @property
    def parameters(self):
        return [
            Parameter(
                [self.instance.klass.name],
                make_internal_token("other")
            )
        ]

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
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntDivide(BaseInternalMethod):
    name = make_internal_token("divide")

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
        from .Float import FloatClass
        
        return FloatClass.name

    def call(self, interpreter, arguments):
        from .Float import FloatInstance, FloatClass

        try:
            if is_instance(interpreter, arguments[0], IntClass.name, FloatClass.name):
                return FloatInstance(interpreter).set_value(
                    self.instance.value / arguments[0].value
                )
        except ZeroDivisionError:
            raise InternalError("Attempted division by zero.")

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntEquals(BaseInternalMethod):
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

        if is_instance(interpreter, arguments[0], IntClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value == arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntGreaterThan(BaseInternalMethod):
    name = make_internal_token("greaterThan")

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

        if is_instance(interpreter, arguments[0], IntClass.name):
            return BoolInstance(interpreter).set_value(
                self.instance.value > arguments[0].value
            )

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class IntNegate(BaseInternalMethod):
    name = make_internal_token("negate")

    def call(self, interpreter, arguments):
        return IntInstance(interpreter).set_value(-self.instance.value)


class IntIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    @property
    def return_token(self):
        return IntClass.name

    def call(self, interpreter, arguments):
        return internal_next(interpreter, range(self.instance.value))


class IntIsTrue(BaseInternalMethod):
    name = make_internal_token("isTrue")

    @property
    def return_token(self):
        from .Bool import BoolClass
        
        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(self.instance.value != 0)


class IntToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from .String import StringClass
        
        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter).set_value(str(self.instance.value))


class IntToFloat(BaseInternalMethod):
    name = make_internal_token("toFloat")

    @property
    def return_token(self):
        from .Float import FloatClass
        
        return FloatClass.name

    def call(self, interpreter, arguments):
        from .Float import FloatInstance

        return FloatInstance(interpreter).set_value(float(self.instance.value))


class IntClass(BaseInternalClass):
    name = make_internal_token("Int")
    FIELDS = (
        IntInit,
        IntAdd,
        IntSubstract,
        IntMultiply,
        IntDivide,
        IntEquals,
        IntGreaterThan,
        IntNegate,
        IntIterate,
        IntIsTrue,
        IntToString,
        IntToFloat,
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
        if isinstance(value, float):
            self.value = int(value)
        elif isinstance(value, int):
            self.value = value
        elif is_instance(self.interpreter, value, IntClass.name):
            self.value = value.value
        else:
            raise InternalError(f"Invalid value passed to {self.class_name}.")

        return self

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, IntInstance):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)
