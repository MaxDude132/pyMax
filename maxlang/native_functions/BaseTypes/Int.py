from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod
from maxlang.errors import InternalError


class IntAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatClass, FloatInstance

        if isinstance(arguments[0], IntInstance):
            return IntInstance(self.instance.klass, self.instance.value + arguments[0].value)
        if isinstance(arguments[0], FloatInstance):
            klass = interpreter.environment.internal_get(FloatClass.name)
            return FloatInstance(klass, self.instance.value + arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntSubstract(BaseInternalMethod):
    name = "substract"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatClass, FloatInstance

        if isinstance(arguments[0], IntInstance):
            return IntInstance(self.instance.klass, self.instance.value - arguments[0].value)
        if isinstance(arguments[0], FloatInstance):
            klass = interpreter.environment.internal_get(FloatClass.name)
            return FloatInstance(klass, self.instance.value - arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatClass, FloatInstance

        if isinstance(arguments[0], IntInstance):
            return IntInstance(self.instance.klass, self.instance.value * arguments[0].value)
        if isinstance(arguments[0], FloatInstance):
            klass = interpreter.environment.internal_get(FloatClass.name)
            return FloatInstance(klass, self.instance.value * arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntDivide(BaseInternalMethod):
    name = "divide"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatClass, FloatInstance

        try:
            if isinstance(arguments[0], IntInstance):
                return IntInstance(self.instance.klass, self.instance.value / arguments[0].value)
            if isinstance(arguments[0], FloatInstance):
                klass = interpreter.environment.internal_get(FloatClass.name)
                return FloatInstance(klass, self.instance.value / arguments[0].value)
        except ZeroDivisionError:
            raise InternalError("Attempted division by zero.")

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if isinstance(arguments[0], IntInstance):
            return IntInstance(self.instance.klass, self.instance.value == arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class IntGreaterThan(BaseInternalMethod):
    name = "greaterThan"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if isinstance(arguments[0], IntInstance):
            return IntInstance(self.instance.klass, self.instance.value > arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class IntNegate(BaseInternalMethod):
    name = "negate"

    def call(self, interpreter, arguments):
        return IntInstance(self.instance.klass, -self.instance.value)


class IntIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        klass = interpreter.environment.internal_get(BoolClass.name)
        return BoolInstance(klass, self.instance.value != 0)


class IntToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringClass, StringInstance

        klass = interpreter.environment.internal_get(StringClass.name)
        return StringInstance(klass, str(self.instance.value))


class IntClass(BaseInternalClass):
    name = "Int"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return IntInstance(self, arguments[0])
    

class IntInstance(BaseInternalInstance):
    FIELDS = (
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

    def __init__(self, klass, value):
        super().__init__(klass)
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        if not isinstance(other, IntInstance):
            return False
        
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
