from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(1.toString())") == "1"


def test_toInt():
    assert run_source("print('1'.toInt())") == "1"
    assert run_source("print('1.0'.toInt())") == "1"
    assert run_source("print('test'.toInt())") == formatted_error(
        "Cannot convert value test to <Int>", 1
    )


def test_toFloat():
    assert run_source("print('1'.toFloat())") == "1.0"
    assert run_source("print('1.0'.toFloat())") == "1.0"
    assert run_source("print('test'.toFloat())") == formatted_error(
        "Cannot convert value test to <Float>", 1
    )


def test_init():
    assert run_source("print(String('test'))") == "test"
    assert run_source("print(String(true))") == "true"


def test_equals():
    assert run_source("print('test'.equals('test'))") == "true"
    assert run_source("print('test'.equals('tes'))") == "false"
    assert run_source("print('test'.equals(1))") == formatted_error(
        "Error at '1': Expected String but got Int for parameter other in call to equals.",
        1,
    )


def test_toBool():
    assert run_source("print('t'.toBool())") == "true"
    assert run_source("print(''.toBool())") == "false"


def test_multiply():
    assert run_source("print('a'.multiply(3))") == "aaa"
    assert run_source("print('a'.multiply('3'))") == formatted_error(
        "Error at ''3'': Expected Int but got String for parameter value in call to multiply.",
        1,
    )
    assert run_source("print('a'.multiply(3.2))") == formatted_error(
        "Error at '3.2': Expected Int but got Float for parameter value in call to multiply.",
        1,
    )


def test_iterate():
    assert run_source("print('test'.iterate())") == "<StringIterator>"


def test_add():
    assert run_source("print('Hello, '.add('world!'))") == "Hello, world!"
    assert run_source("print('Number: '.add(42))") == "Number: 42"
    assert run_source("print('Value: '.add(3.14))") == "Value: 3.14"
    assert run_source("print('Test'.add(true))") == "Testtrue"
    assert run_source("print('Test' + false)") == "Testfalse"
    assert run_source("""
class WithoutToString {}
print('Value: '.add(WithoutToString()))
""") == formatted_error(
        "Error at 'WithoutToString': <class WithoutToString> does not have required method 'toString'.",
        3,
    )


def test_to_upper():
    assert run_source("print('test'.toUpper())") == "TEST"
    assert run_source("print('TeSt123!'.toUpper())") == "TEST123!"


def test_to_lower():
    assert run_source("print('TEST'.toLower())") == "test"
    assert run_source("print('TeSt123!'.toLower())") == "test123!"
