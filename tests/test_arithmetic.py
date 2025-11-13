from .main import run_source, formatted_error


def test_addition():
    assert run_source("print(1 + 1)") == "2"
    assert run_source("print(1 + 1.0)") == "2.0"
    assert run_source("print(1.0 + 1)") == "2.0"
    assert run_source("print(1.1 + 1.2)") == "2.3"
    assert run_source("print('test' + 1)") == "test1"
    assert run_source("print('test' + ' other_test')") == "test other_test"
    # assert run_source("print(1 + 'test')") == formatted_error(
    #     "Error at ''test'': Expected Int but got String for parameter other in call to add.",
    #     1,
    # )
    assert run_source("print(true + true)") == formatted_error(
        "Error at '+': <class Bool> does not implement the add method.", 1
    )
    assert run_source("print('true' + true)") == "truetrue"
    assert run_source("print(List(1) + List(2))") == "List(1, 2)"
    assert run_source("print(List(1) + 2)") == formatted_error(
        "Error at '2': Expected List but got Int for parameter other in call to add.", 1
    )
    assert (
        run_source("print(Map(1 -> 'test') + Map(2 -> 'test2'))")
        == 'Map(1 -> "test", 2 -> "test2")'
    )
    assert run_source("print(Map(1 -> 'test') + 2 -> 'test2')") == formatted_error(
        "Can only add maps or pairs to maps.", 1
    )  # Addition has priority over pair
    # assert (
    #     run_source("print(Map(1 -> 'test') + (2 -> 'test2'))")
    #     == "Map(1 -> \"test\", 2 -> \"test2\")"
    # )


def test_substraction():
    assert run_source("print(2 - 1)") == "1"
    # assert run_source("print(2 - 1.0)") == "1.0"
    # assert run_source("print(2.0 - 1)") == "1.0"
    assert (
        run_source("print(2.3 - 1.2)") == "1.0999999999999999"
    )  # Floating point edge case
    assert run_source("print('test' - 't')") == formatted_error(
        "Error at '-': <class String> does not implement the substract method.", 1
    )
    assert run_source("print(true - 't')") == formatted_error(
        "Error at '-': <class Bool> does not implement the substract method.", 1
    )
    assert run_source("print(List(1, 2) - 1)") == formatted_error(
        "Error at '-': <class List> does not implement the substract method.", 1
    )
    assert run_source("print(Map(1 -> 'test') - 1)") == formatted_error(
        "Error at '-': <class Map> does not implement the substract method.", 1
    )
    assert run_source("print((1 -> 'test') - 1)") == formatted_error(
        "Error at '-': <class Pair> does not implement the substract method.", 1
    )


def test_multiplication():
    assert run_source("print(2 * 1)") == "2"
    # assert run_source("print(2 * 1.0)") == "2.0"
    # assert run_source("print(2.0 * 1)") == "2.0"
    assert run_source("print(2.3 * 1.2)") == "2.76"  # Floating point edge case
    assert run_source("print('test' * 't')") == formatted_error(
        "Error at ''t'': Expected Int but got String for parameter value in call to multiply.",
        1,
    )
    assert run_source("print('test' * 2)") == "testtest"
    assert run_source("print(true * 't')") == formatted_error(
        "Error at '*': <class Bool> does not implement the multiply method.", 1
    )
    assert run_source("print(List(1, 2) * 2)") == "List(1, 2, 1, 2)"
    assert run_source("print(Map(1 -> 'test') * 2)") == formatted_error(
        "Error at '*': <class Map> does not implement the multiply method.", 1
    )
    assert run_source("print((1 -> 'test') * 2)") == formatted_error(
        "Error at '*': <class Pair> does not implement the multiply method.", 1
    )


def test_division():
    assert run_source("print(4 / 2)") == "2.0"
    # assert run_source("print(4 / 2.0)") == "2.0"
    # assert run_source("print(4.0 / 2)") == "2.0"
    assert (
        run_source("print(2.3 / 1.2)") == "1.9166666666666665"
    )  # Floating point edge case
    assert run_source("print('test' / 't')") == formatted_error(
        "Error at '/': <class String> does not implement the divide method.", 1
    )
    assert run_source("print(true / 't')") == formatted_error(
        "Error at '/': <class Bool> does not implement the divide method.", 1
    )
    assert run_source("print(List(1, 2) / 1)") == formatted_error(
        "Error at '/': <class List> does not implement the divide method.", 1
    )
    assert run_source("print(Map(1 -> 'test') / 1)") == formatted_error(
        "Error at '/': <class Map> does not implement the divide method.", 1
    )
    assert run_source("print((1 -> 'test') / 1)") == formatted_error(
        "Error at '/': <class Pair> does not implement the divide method.", 1
    )
