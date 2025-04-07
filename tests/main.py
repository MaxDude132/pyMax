from contextlib import redirect_stdout, redirect_stderr
from maxlang import Max
import io


def run_source(source) -> str:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        Max().run_source(source)
    return out.getvalue().strip() or err.getvalue().strip()


def formatted_error(message, line):
    return f"[line {line}] {message}"
