from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print((1 -> 'test').toString())") == 'Pair(1, "test")'


def test_init():
    assert run_source("print(Pair(1, true))") == "Pair(1, true)"
    assert run_source("print(Pair(1.3))") == formatted_error("Error at 'Pair': Expected between 2 and 2 arguments in call to Pair but got 1.", 1)


def test_first():
    assert run_source("print((1 -> true).first)") == "1"


def test_second():
    assert run_source("print((1 -> true).second)") == "true"


def test_is_true():
    assert run_source("print((1 -> true).isTrue())") == formatted_error("Error at 'isTrue': Function isTrue not found.", 1)
