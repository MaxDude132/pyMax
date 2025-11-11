from ..main import (
    BaseInternalClass,
    BaseInternalMethod,
    BaseInternalInstance,
    is_instance,
    make_internal_token,
)
from maxlang.errors import InternalError
from maxlang.parse.expressions import Parameter


class ListInit(BaseInternalMethod):
    name = make_internal_token("init")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("items"), is_varargs=True)]

    def call(self, interpreter, arguments):
        self.instance.set_values(*arguments[0].values)


class ListPush(BaseInternalMethod):
    name = make_internal_token("push")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    def call(self, interpreter, arguments):
        self.instance.values.append(arguments[0])


class ListPop(BaseInternalMethod):
    name = make_internal_token("pop")

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        try:
            return self.instance.values.pop()
        except IndexError:
            raise InternalError(f"No more items in {self.instance.class_name}.")


class ListGet(BaseInternalMethod):
    name = make_internal_token("get")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [IntClass.name]

    @property
    def return_token(self):
        from .Object import ObjectClass

        return ObjectClass.name

    def call(self, interpreter, arguments):
        try:
            return self.instance.values[int(arguments[0].value)]
        except (ValueError, IndexError, TypeError, AttributeError):
            raise InternalError(f"{arguments[0]} is not a valid index.")


class ListExtend(BaseInternalMethod):
    name = make_internal_token("extend")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [ListClass.name]

    def call(self, interpreter, arguments):
        if not is_instance(interpreter, arguments[0], ListClass.name):
            raise InternalError(
                "Can only extend a List with another list. Use push to add an item to a List."
            )

        if arguments[0] == self.instance:
            raise InternalError("Cannot extend a List with itself.")

        self.instance.extend(arguments[0].values)


class ListIterate(BaseInternalMethod):
    name = make_internal_token("iterate")

    @property
    def return_token(self):
        from ..Interators.ListIterator import ListIteratorClass

        return ListIteratorClass.name

    def call(self, interpreter, arguments):
        from ..Interators.ListIterator import ListIteratorInstance

        return ListIteratorInstance(interpreter).set_value(self.instance)


class ListAdd(BaseInternalMethod):
    name = make_internal_token("add")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [ListClass.name]

    def call(self, interpreter, arguments):
        if is_instance(interpreter, arguments[0], ListClass.name):
            new_list = ListInstance(interpreter).set_values(*self.instance.values)
            new_list.extend(arguments[0].values)
            return new_list

        raise InternalError(
            "Can only add a List to a List. Use the push method to add items to a List."
        )


class ListMultiply(BaseInternalMethod):
    name = make_internal_token("multiply")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        from .Int import IntClass

        return [IntClass.name]

    def call(self, interpreter, arguments):
        from .Int import IntClass

        if is_instance(interpreter, arguments[0], IntClass.name):
            return ListInstance(interpreter).set_values(
                *(self.instance.values * arguments[0].value)
            )

        raise InternalError(
            f"Cannot {self.name.lexeme} {self.instance.class_name} and {arguments[0].class_name}"
        )


class ListEquals(BaseInternalMethod):
    name = make_internal_token("equals")

    @property
    def parameters(self):
        return [Parameter(make_internal_token("other"))]

    @property
    def allowed_types(self):
        return [ListClass.name]

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        if is_instance(interpreter, arguments[0], ListClass.name):
            return BoolInstance(interpreter).set_value(self.instance == arguments[0])

        raise InternalError(
            f"Cannot compare {self.instance.class_name} and {arguments[0].class_name}"
        )


class ListToBool(BaseInternalMethod):
    name = make_internal_token("toBool")

    @property
    def return_token(self):
        from .Bool import BoolClass

        return BoolClass.name

    def call(self, interpreter, arguments):
        from .Bool import BoolInstance

        return BoolInstance(interpreter).set_value(len(self.instance.values) != 0)


class ListToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from .String import StringClass

        return StringClass.name

    def call(self, interpreter, arguments):
        from .String import StringInstance

        stringified = (
            self.instance.klass.interpreter.stringify(v, True)
            for v in self.instance.values
        )
        return StringInstance(interpreter).set_value(
            f"{self.instance.klass.name.lexeme}({', '.join(stringified)})"
        )


class ListClass(BaseInternalClass):
    name = make_internal_token("List")
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
        ListToBool,
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
