from .main import BaseInternalClass


NEXT_SENTINEL = object()


class Next(BaseInternalClass):
    name = "next"

    def lower_arity(self):
        return 2
    
    def upper_arity(self):
        return 2
    
    def init(self):
        self.currrent = None
        self.next = None

    def call(self, interpreter, arguments):
        self.current = arguments[0]
        self.next = arguments[1]
        return self
