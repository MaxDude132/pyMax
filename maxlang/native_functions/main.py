from __future__ import annotations
from typing import TYPE_CHECKING

from maxlang.parse.callable import InternalCallable
from maxlang.lex import Token
from maxlang.errors import InterpreterError, InternalError
from maxlang.parse.expressions import Lambda

if TYPE_CHECKING:
    from maxlang.parse.interpreter import Interpreter


def format_class_name(name: str):
    return f"<{name}>"


class BaseInternalFunction(InternalCallable):
    name = ""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        if hasattr(self, "init"):
            self.init()
    
    @property
    def declaration(self):
        return Lambda([], [])


class BaseInternalClass(InternalCallable):
    name = ""
    
    def get_class(self):
        return self
    
    @property
    def class_name(self):
        return format_class_name("class " + self.get_class().name)

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        if hasattr(self, "init"):
            self.init()

    def check_arity(self, arg_count):
        return arg_count >= self.lower_arity() and arg_count <= self.upper_arity()
    
    def upper_arity(self):
        return 0
    
    def lower_arity(self):
        return 0
    
    def __str__(self) -> str:
        return f"<class {self.name}>"


class BaseInternalMethod(InternalCallable):
    name = ""
    
    def get_class(self):
        return self.instance.klass
    
    @property
    def class_name(self):
        return format_class_name(f"{self.get_class().name}.{self.name}")
    
    def return_self(self):
        return self.instance

    def __init__(self, instance: BaseInternalClass):
        self.instance = instance

    def __str__(self):
        return f"<method '{self.name}' of class '{self.instance.class_name}'>"
    

class BaseInternalAttribute(InternalCallable):
    name = ""
    
    @property
    def class_name(self):
        return format_class_name(f"{self.get_class().name}.{self.name}")
    
    def get_class(self):
        return self.instance.klass

    def __init__(self, instance: BaseInternalClass):
        self.instance = instance

    def __str__(self):
        return f"<attribute '{self.name}' of class '{self.instance.name}'>"
    

# Methods shared by all class instances
class SharedIsNotTrue(BaseInternalMethod):
    name = "isNotTrue"

    def call(self, interpreter, arguments):
        from .BaseTypes.Bool import BoolInstance, BoolClass

        try:
            klass = interpreter.environment.internal_get(BoolClass.name)
            bool_value = self.instance.internal_find_method("isTrue").call(interpreter, [])
            return BoolInstance(klass, not bool_value.value)
        except KeyError:
            raise InternalError(f"class {self.class_name} does not implement the isTrue method.")


class BaseInternalInstance(InternalCallable):
    FIELDS = ()
    __COMMON_FIELDS = (
        SharedIsNotTrue,
    )

    def __init__(self, klass: BaseInternalClass):
        self.klass = klass
        self._fields = {m.name: m(self) for m in self.__COMMON_FIELDS}
        self._fields.update({m.name: m(self) for m in self.FIELDS})
    
    def find_method(self, name: Token):
        if name.lexeme not in self._fields:
            raise InterpreterError(name, f"Field '{name.lexeme}' on class '{self.class_name}' not found.")
        
        ret = self._fields[name.lexeme]
        if isinstance(ret, BaseInternalAttribute):
            ret = ret.call(self.interpreter, [])

        return ret
    
    def internal_find_method(self, name: str):
        return self._fields[name]
    
    @property
    def class_name(self):
        return format_class_name(self.get_class().name)
    
    def get_class(self):
        return self.klass
