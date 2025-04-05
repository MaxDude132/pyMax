from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod
from maxlang.errors import InternalError


class BoolEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if isinstance(arguments[0], BoolInstance):
            return BoolInstance(interpreter, self.instance.value is arguments[0].value)

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class BoolIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        return BoolInstance(interpreter, self.instance.value)


class BoolToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        return StringInstance(interpreter, "true" if self.instance.value else "false")


class BoolClass(BaseInternalClass):
    name = "Bool"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return BoolInstance(interpreter, arguments[0])
    

class BoolInstance(BaseInternalInstance):
    CLASS = BoolClass
    FIELDS = (
        BoolEquals,
        BoolIsTrue,
        BoolToString,
    )

    def __init__(self, interpreter, value: bool):
        super().__init__(interpreter)
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        if not isinstance(other, BoolInstance):
            return False
        
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
