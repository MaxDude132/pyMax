from .main import BaseInternalFunction

import time


class Clock(BaseInternalFunction):
    name = "clock"

    def check_arity(self, arg_count):
        return arg_count == 0
    
    def upper_arity(self):
        return 0
    
    def lower_arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return time.time()