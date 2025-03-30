from .main import BaseInternalFunction


class Print(BaseInternalFunction):
    name = "print"
    
    def upper_arity(self):
        return float("inf")
    
    def call(self, interpreter, arguments):
        print(*arguments)