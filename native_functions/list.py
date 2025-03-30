from .main import BaseInternalClass, BaseInternalMethod
from .next import Next, NEXT_SENTINEL


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
    

class ListIterate(BaseInternalMethod):
    name = "iterate"

    def call(self, interpreter, arguments):
        iters = []
        previous = None
        for value in self.instance.values:
            if previous is not None:
                iters.append(Next(interpreter).call(interpreter, [previous, value]))

            previous = value

        iters.append(Next(interpreter).call(interpreter, [previous, NEXT_SENTINEL]))

        return iters


class List(BaseInternalClass):
    name = "list"

    METHODS = [
        ListAdd,
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
