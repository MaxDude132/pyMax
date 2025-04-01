from ..main import BaseInternalClass, BaseInternalAttribute, BaseInternalInstance, BaseInternalMethod
from errors import InternalError


class PairFirst(BaseInternalAttribute):
    name = "first"

    def call(self, interpreter, arguments):
        return self.instance.first


class PairSecond(BaseInternalAttribute):
    name = "second"

    def call(self, interpreter, arguments):
        return self.instance.second


class PairEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if isinstance(arguments[0], PairInstance):
            return PairInstance(self.instance.klass, self.instance == arguments[0])

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class PairToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringClass, StringInstance

        klass = interpreter.environment.internal_get(StringClass.name)
        stringified = f"{self.instance.class_name}({self.instance.klass.interpreter.stringify(self.instance.first, True)}, {self.instance.klass.interpreter.stringify(self.instance.second, True)})"
        return StringInstance(klass, f"{self.instance.klass.name}({stringified})")


class PairClass(BaseInternalClass):
    name = "Pair"

    def lower_arity(self):
        return 2
    
    def upper_arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        return PairInstance(self, arguments[0], arguments[1])
    

class PairInstance(BaseInternalInstance):
    FIELDS = (
        PairFirst,
        PairSecond,
        PairEquals,
        PairToString
    )

    def __init__(self, klass, first, second):
        super().__init__(klass)
        self.first = first
        self.second = second
    
    def __str__(self):
        return self.internal_find_method("toString").call(self.klass.interpreter, [])
    
    def __eq__(self, other):
        if not isinstance(other, PairInstance):
            return False
        
        return self.first == other.first and self.second == other.second
    
    def __hash__(self):
        return hash(str(self))
