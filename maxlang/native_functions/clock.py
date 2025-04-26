from .main import BaseInternalFunction, make_internal_token

import time


class Clock(BaseInternalFunction):
    name = make_internal_token("clock")

    def call(self, interpreter, arguments):
        return time.time()
