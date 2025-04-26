from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(true.toString())") == "true"
    assert run_source("print(false.toString())") == "false"


def test_init():
    assert run_source("print(Bool(true))") == "true"
    assert run_source("print(Bool(false))") == "false"
    assert run_source("print(Bool(1))") == formatted_error("Error at '1': Expected Bool but got Int for parameter value in call to Bool.", 1)
    assert run_source("print(Bool(\"test\"))") == formatted_error("Error at '\"test\"': Expected Bool but got String for parameter value in call to Bool.", 1)


def test_equals():
    assert run_source("print(true.equals(false))") == "false"
    assert run_source("print(false.equals(false))") == "true"
    assert run_source("print(false.equals(1))") == formatted_error("Error at '1': Expected Bool but got Int for parameter other in call to equals.", 1)


def test_is_true():
    assert run_source("print(true.isTrue())") == "true"
    assert run_source("print(false.isTrue())") == "false"
