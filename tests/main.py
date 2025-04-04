from contextlib import redirect_stdout
import pytest
from maxlang import Max
import io


def run_source(source) -> str:
    string = io.StringIO()
    with redirect_stdout(string):
        Max().run_source(source)
    return string.getvalue().strip()


def formatted_error(message, line):
    return f"{message}\n[line {line}]"
    