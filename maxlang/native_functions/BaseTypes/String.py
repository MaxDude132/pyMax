from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod
from maxlang.errors import InternalError


class StringAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        from .Float import FloatInstance
        
        if isinstance(arguments[0], (IntInstance, FloatInstance, StringInstance)):
            return StringInstance(self.instance.klass, self.instance.value + str(arguments[0].value))

        raise InternalError(f"Cannot add {self.instance.class_name} and {arguments[0].class_name}")


class StringMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        
        if isinstance(arguments[0], (IntInstance,)):
            return StringInstance(self.instance.klass, self.instance.value * arguments[0].value)

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class StringEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        if isinstance(arguments[0], StringInstance):
            klass = interpreter.environment.internal_get(BoolClass.name)
            return BoolInstance(klass, self.instance.value == arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class StringIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        klass = interpreter.environment.internal_get(BoolClass.name)
        return BoolInstance(klass, len(self.instance.value) != 0)


class StringToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        return StringInstance(self.instance.klass, self.instance.value)


class StringClass(BaseInternalClass):
    name = "String"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return StringInstance(self, arguments[0])
    

class StringInstance(BaseInternalInstance):
    FIELDS = (
        StringAdd,
        StringMultiply,
        StringEquals,
        StringIsTrue,
        StringToString,
    )

    def __init__(self, klass, value):
        super().__init__(klass)
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        if not isinstance(other, StringInstance):
            return False
        
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

