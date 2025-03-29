from parse.callable import InternalCallable

import time


class Clock(InternalCallable):
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return time.time()