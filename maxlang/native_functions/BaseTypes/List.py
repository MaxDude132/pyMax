from ..main import BaseInternalClass, BaseInternalMethod, BaseInternalInstance, is_instance
from ..next import internal_next
from maxlang.errors import InternalError


class ListInit(BaseInternalMethod):
    name = "init"

    def lower_arity(self):
        return 0

    def upper_arity(self):
        return float("inf")

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments)


class ListPush(BaseInternalMethod):
    name = "push"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        self.instance.values.append(arguments[0])


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
        if not is_instance(interpreter, arguments[0], ListClass.name):
            raise InternalError(
                "Can only extend a List with another list. Use push to add an item to a List."
            )

        if arguments[0] == self.instance:
            raise InternalError("Cannot extend a List with itself.")

        self.instance.extend(arguments[0].values)


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
        if is_instance(interpreter, arguments[0], ListClass.name):
            new_list = ListInstance(interpreter).set_values(*self.instance.values)
            new_list.extend(arguments[0].values)
            return new_list

        raise InternalError(
            "Can only add a List to a List. Use the push method to add items to a List."
        )


class ListMultiply(BaseInternalMethod):
    name = "multiply"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return ListInstance(interpreter).set_values(
                *(self.instance.values * arguments[0].value)
            )

        raise InternalError(
            f"Cannot {self.name} {self.instance.class_name} and {arguments[0].class_name}"
        )


class ListEquals(BaseInternalMethod):
    name = "equals"

    def lower_arity(self):
        return 1

    def upper_arity(self):
        return 1

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], ListClass.name):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class ListIsTrue(BaseInternalMethod):
    name = "isTrue"

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.values) != 0)


class ListToString(BaseInternalMethod):
    name = "toString"

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (
            self.instance.klass.interpreter.stringify(v, True)
            for v in self.instance.values
        )
        return StringInstance(interpreter).set_value(
            f"{self.instance.klass.name}({", ".join(stringified)})"
        )


class ListClass(BaseInternalClass):
    name = "List"
    FIELDS = (
        ListInit,
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
    )

    @property
    def instance_class(self):
        return ListInstance

    def upper_arity(self):
        return float("inf")


class ListInstance(BaseInternalInstance):
    CLASS = ListClass

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.values = []

    def set_values(self, *args):
        self.values = [*args]
        return self

    def __str__(self) -> str:
        return self.internal_find_method("toString").call(self.interpreter, [])

    def extend(self, other_list):
        self.values.extend(other_list)

    def __eq__(self, other):
        if not isinstance(other, ListInstance):
            return False

        return self.values == other.values

    def __hash__(self):
        return hash(str(self))
