from __future__ import annotations
from typing import Any, TYPE_CHECKING

from .expressions import Lambda
from .environment import Environment
from lex import Token, TokenType
from errors import InterpreterError

if TYPE_CHECKING:
    from .interpreter import Interpreter


class Return(Exception):
    def __init__(self, value):
        self.value = value


class InternalCallable:
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any | None:
        pass

    def arity(self) -> int:
        pass

    def __str__(self) -> str:
        func_name = ''.join(
            '_' + char.lower() if char.isupper() else char
            for char in self.__class__.__name__
        ).lstrip('_')
        return f"<function {func_name}>"


class FunctionCallable(InternalCallable):
    def __init__(self, name: str, declaration: Lambda, closure: Environment, class_instance: InstanceCallable | None = None):
        self.name = name
        self.declaration = declaration
        self.closure = closure
        self.class_instance = class_instance

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        environment = Environment(self.closure)
        for i, argument in enumerate(arguments):
            environment.define(self.declaration.params[i], argument)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as ret:
            if ret.value is None:
                return self.return_self()

            return ret.value
        
        return self.return_self()

    def arity(self):
        return len(self.declaration.params)

    def bind(self, instance: InstanceCallable) -> FunctionCallable:
        environment = Environment(self.closure)
        environment.define(Token(TokenType.IDENTIFIER, "this", None, -1), instance)
        return FunctionCallable(self.name, self.declaration, environment, instance)
    
    def return_self(self) -> Any | None:
        if self.class_instance is not None:
            return self.closure.get_at(0, "this")

    def __str__(self) -> str:
        if self.name is not None:
            return f"<function {self.name}>"
        else:
            return "<lambda>"


class ClassCallable(InternalCallable):
    def __init__(self, name: str, superclasses: list[ClassCallable], methods: dict[str, FunctionCallable]):
        self.name = name
        self.superclasses = superclasses
        self.methods = methods

    def call(self, interpreter, arguments) -> InstanceCallable:
        instance = InstanceCallable(self)
        initialiser = self.find_method(Token(None, "init", None, None))
        if initialiser is not None:
            initialiser.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self):
        initialiser = self.find_method(Token(None, "init", None, None))
        if initialiser is None:
            return 0
        return initialiser.arity()
    
    def find_method(self, name: Token, check_supers: bool = True, errored: bool = False) -> FunctionCallable | None:
        if name.lexeme in self.methods:
            return self.methods.get(name.lexeme)
        
        if not check_supers and not errored and name.lexeme != "init":
            for superclass in self.superclasses:
                value = superclass.find_method(name, errored=True)
                if value is not None:
                    raise InterpreterError(name, f"Field {name.lexeme} found in superclass to one of the superclasses. Inherit from class {superclass.name} to gain access to this field.")
            
            raise InterpreterError(name, f"Field {name.lexeme} not found in superclasses.")
        
        value = None
        for superclass in self.superclasses:
            value = superclass.find_method(name, check_supers=False, errored=errored)
            if value is not None:
                return value

    def __str__(self) -> str:
        return f"<class {self.name}>"


class InstanceCallable(InternalCallable):
    def __init__(self, klass: ClassCallable):
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name)
        if method is not None:
            return method.bind(self)
        
        raise InterpreterError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"<instanceof {self.klass.name}>"


