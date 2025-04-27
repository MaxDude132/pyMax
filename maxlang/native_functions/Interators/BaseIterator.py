from ..main import BaseInternalClass, BaseInternalInstance, BaseInternalMethod, make_internal_token


class IteratorToString(BaseInternalMethod):
    name = make_internal_token("toString")

    @property
    def return_token(self):
        from ..BaseTypes.String import StringClass
        
        return StringClass.name

    def call(self, interpreter, arguments):
        from ..BaseTypes.String import StringInstance

        return StringInstance(interpreter).set_value(f"{self.instance.class_name}")


class BaseIteratorClass(BaseInternalClass):
    _COMMON_FIELDS = BaseInternalClass._COMMON_FIELDS + (
        IteratorToString,
    )


class BaseIteratorInstance(BaseInternalInstance):
    pass
