from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(1.toString())") == "1"


def test_toInt():
    assert run_source("print('1'.toInt())") == "1"
    assert run_source("print('1.0'.toInt())") == "1"
    assert run_source("print('test'.toInt())") == formatted_error("Cannot convert value test to <Int>", 1)


def test_toFloat():
    assert run_source("print('1'.toFloat())") == "1.0"
    assert run_source("print('1.0'.toFloat())") == "1.0"
    assert run_source("print('test'.toFloat())") == formatted_error("Cannot convert value test to <Float>", 1)


def test_init():
    assert run_source("print(String('test'))") == "test"
    assert run_source("print(String(true))") == formatted_error("Error at 'true': Expected String but got Bool for parameter value in call to String.", 1)


def test_equals():
    assert run_source("print('test'.equals('test'))") == "true"
    assert run_source("print('test'.equals('tes'))") == "false"
    assert run_source("print('test'.equals(1))") == formatted_error("Error at '1': Expected String but got Int for parameter other in call to equals.", 1)


def test_is_true():
    assert run_source("print('t'.isTrue())") == "true"
    assert run_source("print(''.isTrue())") == "false"


def test_multiply():
    assert run_source("print('a'.multiply(3))") == "aaa"
    assert run_source("print('a'.multiply('3'))") == formatted_error("Error at ''3'': Expected Int but got String for parameter value in call to multiply.", 1)
    assert run_source("print('a'.multiply(3.2))") == formatted_error("Error at '3.2': Expected Int but got Float for parameter value in call to multiply.", 1)


def test_iterate():
    assert run_source("print('test'.iterate())") == "<StringIterator>"
