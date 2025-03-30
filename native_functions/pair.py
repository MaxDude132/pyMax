from .main import BaseInternalClass, BaseInternalAttribute


class PairFirst(BaseInternalAttribute):
    name = "first"

    def call(self, interpreter, arguments):
        return self.instance.first


class PairSecond(BaseInternalAttribute):
    name = "second"

    def call(self, interpreter, arguments):
        return self.instance.second


class Pair(BaseInternalClass):
    name = "pair"

    FIELDS = (
        PairFirst,
        PairSecond,
    )

    def init(self):
        self.first = None
        self.second = None

    def lower_arity(self):
        return 2
    
    def upper_arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        self.first = arguments[0]
        self.second = arguments[1]
        return self
    
    def __str__(self):
        return f"pair({self.interpreter.stringify(self.first, True)}, {self.interpreter.stringify(self.second, True)})"