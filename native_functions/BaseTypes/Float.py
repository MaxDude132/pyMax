from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod
from errors import InternalError


class FloatAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        
        if isinstance(arguments[0], (IntInstance, FloatInstance)):
            return FloatInstance(self.instance.klass, self.instance.value + arguments[0].value)

        raise InternalError(f"Cannot add {self.instance.class_name} and {arguments[0].class_name}")


class FloatSubstract(BaseInternalMethod):
    name = "substract"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        
        if isinstance(arguments[0], (IntInstance, FloatInstance)):
            return FloatInstance(self.instance.klass, self.instance.value - arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class FloatMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        
        if isinstance(arguments[0], (IntInstance, FloatInstance)):
            return FloatInstance(self.instance.klass, self.instance.value + arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class FloatDivide(BaseInternalMethod):
    name = "divide"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        
        if isinstance(arguments[0], (IntInstance, FloatInstance)):
            try:
                return FloatInstance(self.instance.klass, self.instance.value / arguments[0].value)
            except ZeroDivisionError:
                raise InternalError("Attempted division by zero.")

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class FloatEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        if isinstance(arguments[0], FloatInstance):
            klass = interpreter.environment.internal_get(BoolClass.name)
            return BoolInstance(klass, self.instance.value == arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class FloatGreaterThan(BaseInternalMethod):
    name = "greaterThan"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        if isinstance(arguments[0], FloatInstance):
            klass = interpreter.environment.internal_get(BoolClass.name)
            return BoolInstance(klass, self.instance.value > arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class FloatNegate(BaseInternalMethod):
    name = "negate"

    def call(self, interpreter, arguments):
        return FloatInstance(self.instance.klass, -self.instance.value)


class FloatToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringClass, StringInstance

        klass = interpreter.environment.internal_get(StringClass.name)
        return StringInstance(klass, str(self.instance.value))


class FloatIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        klass = interpreter.environment.internal_get(BoolClass.name)
        return BoolInstance(klass, self.instance.value != 0.0)


class FloatClass(BaseInternalClass):
    name = "Float"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return FloatInstance(self, arguments[0])
    

class FloatInstance(BaseInternalInstance):
    FIELDS = (
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

    def __init__(self, klass, value):
        super().__init__(klass)
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        if not isinstance(other, FloatInstance):
            return False
        
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
