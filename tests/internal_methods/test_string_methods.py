from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(1.toString())") == "1"


def test_init():
    assert run_source("print(String(true))") == "true"
    assert run_source("print(String(false))") == "false"
    assert run_source("print(String(1))") == "1"
    assert run_source("print(String(0))") == "0"


def test_equals():
    assert run_source("print('test'.equals('test'))") == "true"
    assert run_source("print('test'.equals('tes'))") == "false"
    assert run_source("print('test'.equals(1))") == formatted_error("Cannot compare <String> and <Int>", 1)


def test_is_true():
    assert run_source("print('t'.isTrue())") == "true"
    assert run_source("print(''.isTrue())") == "false"


def test_multiply():
    assert run_source("print('a' * 3)") == "aaa"
    assert run_source("print('a' * '3')") == formatted_error("Cannot multiply <String> and <String>", 1)
    assert run_source("print('a' * 3.2)") == formatted_error("Cannot multiply <String> and <Float>", 1)
