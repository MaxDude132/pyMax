from __future__ import annotations
from typing import TYPE_CHECKING

from .main import BaseInternalClass, BaseInternalInstance, BaseInternalAttribute, make_internal_token

if TYPE_CHECKING:
    from maxlang.parse.interpreter import Interpreter


class NextSentinel:
    def __str__(self):
        return "NEXT_SENTINEL"


NEXT_SENTINEL = NextSentinel()


def internal_next(interpreter: Interpreter, values):
    first = None
    previous = None
    sentinel = NextInstance(interpreter, NEXT_SENTINEL, NEXT_SENTINEL)
    for value in values:
        current = NextInstance(interpreter, value, sentinel)

        if previous is not None:
            previous.next_node = current

        previous = current

        if first is None:
            first = current

    return first or sentinel


class NextValue(BaseInternalAttribute):
    name = make_internal_token("first")
    instance: NextInstance

    def call(self, interpreter, arguments):
        return self.instance.value


class NextNextNode(BaseInternalAttribute):
    name = make_internal_token("next_node")
    instance: NextInstance

    def call(self, interpreter, arguments):
        return self.instance.second


class NextClass(BaseInternalClass):
    name = make_internal_token("Next")

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
    CLASS = NextClass
    FIELDS = (
        NextValue,
        NextNextNode,
    )

    def __init__(self, interpreter, value, next_node):
        super().__init__(interpreter)
        self.value = value
        self.next_node = next_node

    def __str__(self):
        return f"{self.class_name}({self.interpreter.stringify(self.value, True)}, {self.next_node})"
