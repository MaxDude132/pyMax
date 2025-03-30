from .main import BaseInternalClass, BaseInternalMethod
from .next import internal_next


class ListAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        self.instance.values.append(arguments[0])


class ListPop(BaseInternalMethod):
    name = "pop"
    
    def call(self, interpreter, arguments):
        return self.instance.values.pop()
    

class ListGet(BaseInternalMethod):
    name = "get"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return self.instance.values[int(arguments[0])]


class ListIterate(BaseInternalMethod):
    name = "iterate"

    def call(self, interpreter, arguments):
        return internal_next(interpreter, self.instance.values)


class List(BaseInternalClass):
    name = "list"

    FIELDS = [
        ListAdd,
        ListGet,
        ListPop,
        ListIterate,
    ]

    def init(self):
        self.values = []

    def upper_arity(self):
        return float("inf")
    
    def call(self, interpreter, arguments):
        for arg in arguments:
            self.values.append(arg)
        return self
    
    def __str__(self) -> str:
        stringified = (self.interpreter.stringify(v, True) for v in self.values)
        return f"list({", ".join(stringified)})"
