from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print('test'.toString())") == "test"


def test_init():
    assert run_source("print(Int(true))") == formatted_error("Invalid value passed to <Int>.", 1)
    assert run_source("print(Int(1))") == "1"
    assert run_source("print(Int(1.3))") == "1"
    assert run_source("print(Int('1'))") == "1"
    assert run_source("print(Int('1.3'))") == formatted_error("Invalid value passed to <Int>.", 1)
    assert run_source("print(Int(Float('1.3')))") == "1"


def test_equals():
    assert run_source("print(1.equals(1))") == "true"
    assert run_source("print(1.equals(2))") == "false"
    assert run_source("print(1.equals(1.0))") == formatted_error("Cannot compare <Int> and <Float>", 1)


def test_is_true():
    assert run_source("print(0.1.isTrue())") == "true"
    assert run_source("print(0.0.isTrue())") == "false"


def test_greater_than():
    assert run_source("print(1.greaterThan(0))") == "true"
    assert run_source("print(0.greaterThan(0))") == "false"
    assert run_source("print(0.greaterThan(true))") == formatted_error("Cannot compare <Int> and <Bool>", 1)


def test_add():
    assert run_source("print(0.add(3))") == "3"
    assert run_source("print(0.add(1.3))") == "1.3"
    assert run_source("print(0.add(true))") == formatted_error("Cannot add <Int> and <Bool>", 1)


def test_substract():
    assert run_source("print(5.substract(3))") == "2"
    assert run_source("print(1.substract(1.5))") == "-0.5"
    assert run_source("print(0.substract(true))") == formatted_error("Cannot substract <Int> and <Bool>", 1)


def test_multiply():
    assert run_source("print(5.multiply(3))") == "15"
    assert run_source("print(0.multiply(1.5))") == "0.0"
    assert run_source("print(0.multiply(true))") == formatted_error("Cannot multiply <Int> and <Bool>", 1)


def test_divide():
    assert run_source("print(5.divide(4))") == "1.25"
    assert run_source("print(0.divide(1.0))") == "0.0"
    assert run_source("print(0.divide(true))") == formatted_error("Cannot divide <Int> and <Bool>", 1)


def test_negate():
    assert run_source("print(1.negate())") == "-1"
