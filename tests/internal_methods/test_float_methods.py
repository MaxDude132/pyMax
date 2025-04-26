from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(1.0.toString())") == "1.0"


def test_init():
    assert run_source("print(Float(1.3))") == "1.3"
    assert run_source("print(Float(true))") == formatted_error("Error at 'true': Expected Float but got Bool for parameter value in call to Float.", 1)


def test_equals():
    assert run_source("print(1.0.equals(1.0))") == "true"
    assert run_source("print(1.3.equals(1.0))") == "false"
    assert run_source("print(1.2.equals(1))") == formatted_error("Error at '1': Expected Float but got Int for parameter other in call to equals.", 1)


def test_is_true():
    assert run_source("print(0.1.isTrue())") == "true"
    assert run_source("print(0.0.isTrue())") == "false"


def test_greater_than():
    assert run_source("print(0.1.greaterThan(0.05))") == "true"
    assert run_source("print(0.0.greaterThan(0.05))") == "false"
    assert run_source("print(0.0.greaterThan(true))") == formatted_error("Error at 'true': Expected Float but got Bool for parameter other in call to greaterThan.", 1)


def test_add():
    assert run_source("print(0.1.add(0.3))") == "0.4"
    assert run_source("print(0.0.add(true))") == formatted_error("Error at 'true': Expected Float but got Bool for parameter other in call to add.", 1)


def test_substract():
    assert run_source("print(0.5.substract(0.3))") == "0.2"
    assert run_source("print(0.0.substract(1.0))") == "-1.0"
    assert run_source("print(0.0.substract(true))") == formatted_error("Error at 'true': Expected Float but got Bool for parameter other in call to substract.", 1)


def test_multiply():
    assert run_source("print(0.5.multiply(0.3))") == "0.15"
    assert run_source("print(0.0.multiply(1.0))") == "0.0"
    assert run_source("print(0.0.multiply(true))") == formatted_error("Error at 'true': Expected Float but got Bool for parameter other in call to multiply.", 1)


def test_divide():
    assert run_source("print(0.5.divide(0.4))") == "1.25"
    assert run_source("print(0.0.divide(1.0))") == "0.0"
    assert run_source("print(0.0.divide(true))") == formatted_error("Error at 'true': Expected Float but got Bool for parameter other in call to divide.", 1)


def test_negate():
    assert run_source("print(0.1.negate())") == "-0.1"
    assert run_source("print((-0.1).negate())") == "0.1"
    assert run_source("print(-0.1.negate())") == "0.1"
