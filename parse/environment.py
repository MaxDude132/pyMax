from __future__ import annotations
from typing import Any

from lex import Token
from errors import InterpreterError


VARIABLE_VALUE_SENTINEL = object()


class Environment:
    def __init__(self, enclosing: Environment | None = None):
        self.values: dict[str, Any] = {}
        self.enclosing = enclosing

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values.get(name.lexeme)
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise InterpreterError(name, f"Undefined variable '{name.lexeme}'.")
    
    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def define(self, name: Token, value: Any = VARIABLE_VALUE_SENTINEL):
        if name.lexeme in self.values:
            raise InterpreterError(name, f"Variable {name.lexeme} already defined.")

        self.values[name.lexeme] = value

    def ancestor(self, distance: int):
        environment = self
        for i in range(distance):
            environment = environment.enclosing

        return environment

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
            
        raise InterpreterError(name, f"Variable {name.lexeme} undefined.")
    
    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).values[name.lexeme] = value
