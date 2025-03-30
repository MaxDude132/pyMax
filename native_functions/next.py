from .main import BaseInternalClass


NEXT_SENTINEL = object()


def internal_next(interpreter, values):
    first = None
    previous = None
    for value in values:
        current = Next(interpreter).internal_set(value, NEXT_SENTINEL)

        if previous is not None:
            previous.next = current

        previous = current

        if first is None:
            first = current

    return first


class Next(BaseInternalClass):
    name = "next"

    def lower_arity(self):
        return 2
    
    def upper_arity(self):
        return 2
    
    def init(self):
        self.value = None
        self.next = None

    def call(self, interpreter, arguments):
        self.value = arguments[0]
        self.next = arguments[1]
        return self
    
    def internal_set(self, value, next_node):
        self.value = value
        self.next = next_node
        return self
