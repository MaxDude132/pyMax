from .main import run_source, formatted_error


def test_convert_to_bool():
    assert run_source("print(Bool(true))") == "true"
    assert run_source("print(Bool(false))") == "false"
    assert run_source("print(Bool(1))") == "true"
    assert run_source("print(Bool(0))") == "false"
    assert run_source("print(Bool('test'))") == "true"
    assert run_source("print(Bool(''))") == "false"
    assert run_source("print(Bool(List(1)))") == "true"
    assert run_source("print(Bool(List()))") == "false"
    assert run_source("print(Bool(Pair(1, 'test')))") == formatted_error(
        "class <Pair> does not implement the isTrue method.", 1
    )
    assert run_source("print(Bool(1 -> 'test'))") == formatted_error(
        "class <Pair> does not implement the isTrue method.", 1
    )
    assert run_source("print(Bool(Map(1 -> 'test')))") == "true"
    assert run_source("print(Bool(Map()))") == "false"
