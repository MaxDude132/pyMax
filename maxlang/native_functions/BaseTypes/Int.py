from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod
from maxlang.errors import InternalError


class IntAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance

        if isinstance(arguments[0], IntInstance):
            return IntInstance(interpreter, self.instance.value + arguments[0].value)
        if isinstance(arguments[0], FloatInstance):
            return FloatInstance(interpreter, self.instance.value + arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntSubstract(BaseInternalMethod):
    name = "substract"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance

        if isinstance(arguments[0], IntInstance):
            return IntInstance(interpreter, self.instance.value - arguments[0].value)
        if isinstance(arguments[0], FloatInstance):
            return FloatInstance(interpreter, self.instance.value - arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance

        if isinstance(arguments[0], IntInstance):
            return IntInstance(interpreter, self.instance.value * arguments[0].value)
        if isinstance(arguments[0], FloatInstance):
            return FloatInstance(interpreter, self.instance.value * arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class IntDivide(BaseInternalMethod):
    name = "divide"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Float import FloatInstance

        try:
            if isinstance(arguments[0], IntInstance):
                return IntInstance(interpreter, self.instance.value / arguments[0].value)
            if isinstance(arguments[0], FloatInstance):
                return FloatInstance(interpreter, self.instance.value / arguments[0].value)
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
        from .Bool import BoolInstance

        if isinstance(arguments[0], IntInstance):
            return BoolInstance(interpreter, self.instance.value == arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class IntGreaterThan(BaseInternalMethod):
    name = "greaterThan"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if isinstance(arguments[0], IntInstance):
            return BoolInstance(interpreter, self.instance.value > arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class IntNegate(BaseInternalMethod):
    name = "negate"

    def call(self, interpreter, arguments):
        return IntInstance(interpreter, -self.instance.value)


class IntIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter, self.instance.value != 0)


class IntToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter, str(self.instance.value))


class IntClass(BaseInternalClass):
    name = "Int"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return IntInstance(interpreter, arguments[0])
    

class IntInstance(BaseInternalInstance):
    CLASS = IntClass
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

    def __init__(self, interpreter, value: int):
        super().__init__(interpreter)
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        if not isinstance(other, IntInstance):
            return False
        
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
