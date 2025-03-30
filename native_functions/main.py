from __future__ import annotations
from typing import TYPE_CHECKING

from parse.callable import InternalCallable
from lex import Token
from errors import InterpreterError

if TYPE_CHECKING:
    from parse.interpreter import Interpreter


class BaseInternalFunction(InternalCallable):
    name = ""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        if hasattr(self, "init"):
            self.init()

    def check_arity(self, arg_count):
        return arg_count >= self.lower_arity() and arg_count <= self.upper_arity()
    
    def upper_arity(self):
        return 0
    
    def lower_arity(self):
        return 0


class BaseInternalClass(InternalCallable):
    name = ""
    METHODS = []

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        if hasattr(self, "init"):
            self.init()

        self._methods = {m.name: m(self) for m in self.METHODS}

    def check_arity(self, arg_count):
        return arg_count >= self.lower_arity() and arg_count <= self.upper_arity()
    
    def upper_arity(self):
        return 0
    
    def lower_arity(self):
        return 0
    
    def get_method(self, name: Token):
        if name.lexeme in self._methods:
            return self._methods[name.lexeme]
        
        raise InterpreterError(name, f"Method '{name.lexeme}' on class '{self.name}' not found.")
    
    def __str__(self) -> str:
        return f"<class {self.name}>"
    

class BaseInternalMethod(InternalCallable):
    name = ""

    def __init__(self, instance: BaseInternalClass):
        self.instance = instance

    def __str__(self):
        return f"<method '{self.name}' of class '{self.instance.name}'>"
