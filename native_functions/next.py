from __future__ import annotations
from typing import TYPE_CHECKING

from .main import BaseInternalClass, BaseInternalInstance, BaseInternalAttribute

if TYPE_CHECKING:
    from parse.interpreter import Interpreter


class NextSentinel:
    def __str__(self):
        return "NEXT_SENTINEL"


NEXT_SENTINEL = NextSentinel()


def internal_next(interpreter: Interpreter, values):
    next_class = interpreter.environment.internal_get(NextClass.name)
    first = None
    previous = None
    sentinel = NextInstance(next_class, NEXT_SENTINEL, NEXT_SENTINEL)
    for value in values:
        current = NextInstance(next_class, value, sentinel)

        if previous is not None:
            previous.next_node = current

        previous = current

        if first is None:
            first = current

    return first or sentinel


class NextValue(BaseInternalAttribute):
    name = "first"
    instance: NextInstance

    def call(self, interpreter, arguments):
        return self.instance.value


class NextNextNode(BaseInternalAttribute):
    name = "next_node"
    instance: NextInstance

    def call(self, interpreter, arguments):
        return self.instance.second


class NextClass(BaseInternalClass):
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
    

class NextInstance(BaseInternalInstance):
    FIELDS = (
        NextValue,
        NextNextNode,
    )

    def __init__(self, klass, value, next_node):
        super().__init__(klass)
        self.value = value
        self.next_node = next_node
    
    def __str__(self):
        return f"{self.class_name}({self.klass.interpreter.stringify(self.value, True)}, {self.next_node})"
