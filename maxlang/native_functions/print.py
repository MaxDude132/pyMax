from .main import BaseInternalFunction, make_internal_token
from maxlang.parse.expressions import Parameter


class Print(BaseInternalFunction):
    name = make_internal_token("print")

    def upper_arity(self):
        return float("inf")
    
    @property
    def parameters(self):
        from .BaseTypes.Object import ObjectClass
        
        return [
            Parameter(
                [ObjectClass.name], 
                make_internal_token("values"), 
                is_varargs=True
            )
        ]

    def call(self, interpreter, arguments):
        stringified = []
        for argument in arguments[0].values:
            stringified.append(interpreter.stringify(argument))
        print(*stringified)
