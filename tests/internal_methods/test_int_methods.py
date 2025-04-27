from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(1.toString())") == "1"


def test_toFloat():
    assert run_source("print(1.toFloat())") == "1.0"


def test_init():
    assert run_source("print(Int(1))") == "1"
    assert run_source("print(Int(true))") == formatted_error("Error at 'true': Expected Int but got Bool for parameter value in call to Int.", 1)


def test_equals():
    assert run_source("print(1.equals(1))") == "true"
    assert run_source("print(1.equals(2))") == "false"
    assert run_source("print(1.equals(1.0))") == formatted_error("Error at '1.0': Expected Int but got Float for parameter other in call to equals.", 1)


def test_is_true():
    assert run_source("print(1.isTrue())") == "true"
    assert run_source("print(0.isTrue())") == "false"


def test_greater_than():
    assert run_source("print(1.greaterThan(0))") == "true"
    assert run_source("print(0.greaterThan(0))") == "false"
    assert run_source("print(0.greaterThan(true))") == formatted_error("Error at 'true': Expected Int but got Bool for parameter other in call to greaterThan.", 1)


def test_add():
    assert run_source("print(0.add(3))") == "3"
    assert run_source("print(0.add(1.3))") == formatted_error("Error at '1.3': Expected Int but got Float for parameter other in call to add.", 1)
    assert run_source("print(0.add(true))") == formatted_error("Error at 'true': Expected Int but got Bool for parameter other in call to add.", 1)


def test_substract():
    assert run_source("print(5.substract(3))") == "2"
    assert run_source("print(1.substract(1.5))") == formatted_error("Error at '1.5': Expected Int but got Float for parameter other in call to substract.", 1)
    assert run_source("print(0.substract(true))") == formatted_error("Error at 'true': Expected Int but got Bool for parameter other in call to substract.", 1)


def test_multiply():
    assert run_source("print(5.multiply(3))") == "15"
    assert run_source("print(0.multiply(1.5))") == formatted_error("Error at '1.5': Expected Int but got Float for parameter other in call to multiply.", 1)
    assert run_source("print(0.multiply(true))") == formatted_error("Error at 'true': Expected Int but got Bool for parameter other in call to multiply.", 1)


def test_divide():
    assert run_source("print(5.divide(4))") == "1.25"
    assert run_source("print(0.divide(1.0))") == formatted_error("Error at '1.0': Expected Int but got Float for parameter other in call to divide.", 1)
    assert run_source("print(0.divide(true))") == formatted_error("Error at 'true': Expected Int but got Bool for parameter other in call to divide.", 1)


def test_negate():
    assert run_source("print(1.negate())") == "-1"


def test_iterate():
    assert run_source("print(2.iterate())") == "<IntIterator>"
