from .main import BaseInternalFunction, make_internal_token


class Print(BaseInternalFunction):
    name = make_internal_token("print")

    def upper_arity(self):
        return float("inf")

    def call(self, interpreter, arguments):
        stringified = []
        for argument in arguments:
            stringified.append(interpreter.stringify(argument))
        print(*stringified)
