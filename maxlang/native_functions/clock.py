from .main import BaseInternalFunction, make_internal_token

import time


class Clock(BaseInternalFunction):
    name = make_internal_token("clock")

    def check_arity(self, arg_count):
        return arg_count == 0

    def upper_arity(self):
        return 0

    def lower_arity(self):
        return 0

    def call(self, interpreter, arguments):
        return time.time()
