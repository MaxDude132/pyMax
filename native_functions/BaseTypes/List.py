from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance
from ..next import internal_next
from errors import InternalError


class ListPush(BaseInternalMethod):
    name = "push"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        self.instance.values.append(arguments[0])
        return self.return_self()


class ListPop(BaseInternalMethod):
    name = "pop"
    
    def call(self, interpreter, arguments):
        return self.instance.values.pop()
    

class ListGet(BaseInternalMethod):
    name = "get"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return self.instance.values[int(arguments[0])]
    

class ListExtend(BaseInternalMethod):
    name = "extend"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], ListInstance):
            raise InternalError("Can only extend a List with another list. Use push to add an item to a List.")
        
        if arguments[0] == self.instance:
            raise InternalError("Cannot extend a List with itself.")

        self.instance.extend(arguments[0].values)
        return self.return_self()


class ListIterate(BaseInternalMethod):
    name = "iterate"

    def call(self, interpreter, arguments):
        return internal_next(interpreter, self.instance.values)


class ListAdd(BaseInternalMethod):
    name = "add"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if isinstance(arguments[0], ListInstance):
            new_list = ListInstance(self.instance.klass, *self.instance.values)
            new_list.extend(arguments[0].values)
            return new_list

        raise InternalError("Can only add a List to a List. Use the push method to add items to a List.")



class ListMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntInstance
        
        if isinstance(arguments[0], (IntInstance,)):
            return ListInstance(self.instance.klass, *(self.instance.values * arguments[0].value))

        raise InternalError(f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}")


class ListEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1
    
    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        if isinstance(arguments[0], ListInstance):
            return ListInstance(self.instance.klass, self.instance == arguments[0])

        raise InternalError(f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}")


class ListIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolClass, BoolInstance

        klass = interpreter.environment.internal_get(BoolClass.name)
        return BoolInstance(klass, len(self.instance.values) != 0)


class ListToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringClass, StringInstance

        klass = interpreter.environment.internal_get(StringClass.name)
        stringified = (self.instance.klass.interpreter.stringify(v, True) for v in self.instance.values)
        return StringInstance(klass, f"{self.instance.klass.name}({", ".join(stringified)})")


class ListClass(BaseInternalClass):
    name = "List"

    def upper_arity(self):
        return float("inf")
    
    def call(self, interpreter, arguments):
        return ListInstance(self, *arguments)
    

class ListInstance(BaseInternalInstance):
    FIELDS = [
        ListPush,
        ListGet,
        ListPop,
        ListExtend,
        ListIterate,
        ListAdd,
        ListMultiply,
        ListEquals,
        ListIsTrue,
        ListToString,
    ]

    def __init__(self, klass,  *args):
        super().__init__(klass)
        self.values = [*args]
    
    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.klass.interpreter, [])
    
    def extend(self, other_list):
        self.values.extend(other_list)
    
    def __eq__(self, other):
        if not isinstance(other, ListInstance):
            return False
        
        return self.values == other.values
    
    def __hash__(self):
        return hash(str(self))
