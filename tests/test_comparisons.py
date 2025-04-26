from .main import run_source, formatted_error


def test_equals():
    assert run_source("print(1 == 1)") == "true"
    assert run_source("print(1 == 2)") == "false"
    assert run_source("print(1 == 1.0)") == formatted_error(
        "Error at '1.0': Expected Int but got Float for parameter other in call to equals.", 1
    )
    assert run_source("print(1.0 == 1)") == formatted_error(
        "Error at '1': Expected Float but got Int for parameter other in call to equals.", 1
    )
    assert run_source("print(1.2 == 1.2)") == "true"
    assert run_source("print(1.1 == 1.2)") == "false"
    assert run_source("print('test' == 1)") == formatted_error(
        "Error at '1': Expected String but got Int for parameter other in call to equals.", 1
    )
    assert run_source("print('test' == 'test')") == "true"
    assert run_source("print('test' == 'other_test')") == "false"
    assert run_source("print(1 == 'test')") == formatted_error(
        "Error at ''test'': Expected Int but got String for parameter other in call to equals.", 1
    )
    assert run_source("print(true == true)") == "true"
    assert run_source("print(false == true)") == "false"
    assert run_source("print('true' == true)") == formatted_error(
        "Error at 'true': Expected String but got Bool for parameter other in call to equals.", 1
    )
    assert run_source("print(List(2) == List(2))") == "true"
    assert run_source("print(List(1) == List(2))") == "false"
    assert run_source("print(List(1) == 2)") == formatted_error(
        "Error at '2': Expected List but got Int for parameter other in call to equals.", 1
    )
    assert run_source("print(Map(1 -> 'test') == Map(1 -> 'test'))") == "true"
    assert run_source("print(Map(1 -> 'test') == Map(2 -> 'test2'))") == "false"
    assert run_source("print(Map(1 -> 'test') == Map(2 -> 'test'))") == "false"
    assert run_source("print(Map(1 -> 'test') == Map(1 -> 'test2'))") == "false"
    assert run_source("print(Map(1 -> 'test') == 2 -> 'test2')") == formatted_error(
        "Error at '->': Expected Map but got Pair for parameter other in call to equals.", 1
    )


def test_not_equals():
    assert run_source("print(1 != 1)") == "false"
    assert run_source("print(1 != 2)") == "true"
    assert run_source("print(1 != 1.0)") == formatted_error(
        "Error at '1.0': Expected Int but got Float for parameter other in call to equals.", 1
    )
    assert run_source("print(1.0 != 1)") == formatted_error(
        "Error at '1': Expected Float but got Int for parameter other in call to equals.", 1
    )
    assert run_source("print(1.2 != 1.2)") == "false"
    assert run_source("print(1.1 != 1.2)") == "true"
    assert run_source("print('test' != 1)") == formatted_error(
        "Error at '1': Expected String but got Int for parameter other in call to equals.", 1
    )
    assert run_source("print('test' != 'test')") == "false"
    assert run_source("print('test' != 'other_test')") == "true"
    assert run_source("print(1 != 'test')") == formatted_error(
        "Error at ''test'': Expected Int but got String for parameter other in call to equals.", 1
    )
    assert run_source("print(true != true)") == "false"
    assert run_source("print(false != true)") == "true"
    assert run_source("print('true' != true)") == formatted_error(
        "Error at 'true': Expected String but got Bool for parameter other in call to equals.", 1
    )
    assert run_source("print(List(2) != List(2))") == "false"
    assert run_source("print(List(1) != List(2))") == "true"
    assert run_source("print(List(1) != 2)") == formatted_error(
        "Error at '2': Expected List but got Int for parameter other in call to equals.", 1
    )
    assert run_source("print(Map(1 -> 'test') != Map(1 -> 'test'))") == "false"
    assert run_source("print(Map(1 -> 'test') != Map(2 -> 'test2'))") == "true"
    assert run_source("print(Map(1 -> 'test') != Map(2 -> 'test'))") == "true"
    assert run_source("print(Map(1 -> 'test') != Map(1 -> 'test2'))") == "true"
    assert run_source("print(Map(1 -> 'test') != 2 -> 'test2')") == formatted_error(
        "Error at '->': Expected Map but got Pair for parameter other in call to equals.", 1
    )


def test_greater():
    assert run_source("print(2 > 1)") == "true"
    assert run_source("print(1 > 1)") == "false"
    assert run_source("print(1 > 1.0)") == formatted_error(
        "Error at '1.0': Expected Int but got Float for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.0 > 1)") == formatted_error(
        "Error at '1': Expected Float but got Int for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.3 > 1.2)") == "true"
    assert run_source("print(1.2 > 1.2)") == "false"
    assert run_source("print('test' > 'test ')") == formatted_error(
        "Error at '>': <String> does not implement the greaterThan method.", 1
    )
    assert run_source("print(1 > 'test')") == formatted_error(
        "Error at ''test'': Expected Int but got String for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(true > true)") == formatted_error(
        "Error at '>': <Bool> does not implement the greaterThan method.", 1
    )
    assert run_source("print(List(2) > List(2))") == formatted_error(
        "Error at '>': <List> does not implement the greaterThan method.", 1
    )
    assert run_source("print(Map(1 -> 'test') > Map(1 -> 'test'))") == formatted_error(
        "Error at '>': <Map> does not implement the greaterThan method.", 1
    )


def test_greater_equals():
    assert run_source("print(2 >= 1)") == "true"
    assert run_source("print(1 >= 1)") == "true"
    assert run_source("print(0 >= 1)") == "false"
    assert run_source("print(1 >= 1.0)") == formatted_error(
        "Error at '1.0': Expected Int but got Float for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.0 >= 1)") == formatted_error(
        "Error at '1': Expected Float but got Int for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.3 >= 1.2)") == "true"
    assert run_source("print(1.2 >= 1.2)") == "true"
    assert run_source("print(1.1 >= 1.2)") == "false"
    assert run_source("print('test' >= 'test ')") == formatted_error(
        "Error at '>=': <String> does not implement the greaterThan method.", 1
    )
    assert run_source("print(1 >= 'test')") == formatted_error(
        "Error at ''test'': Expected Int but got String for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(true >= true)") == formatted_error(
        "Error at '>=': <Bool> does not implement the greaterThan method.", 1
    )
    assert run_source("print(List(2) >= List(2))") == formatted_error(
        "Error at '>=': <List> does not implement the greaterThan method.", 1
    )
    assert run_source("print(Map(1 -> 'test') >= Map(1 -> 'test'))") == formatted_error(
        "Error at '>=': <Map> does not implement the greaterThan method.", 1
    )


def test_lesser():
    assert run_source("print(0 < 1)") == "true"
    assert run_source("print(1 < 1)") == "false"
    assert run_source("print(1 < 1.0)") == formatted_error(
        "Error at '1.0': Expected Int but got Float for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.0 < 1)") == formatted_error(
        "Error at '1': Expected Float but got Int for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.1 < 1.2)") == "true"
    assert run_source("print(1.2 < 1.2)") == "false"
    assert run_source("print('test' < 'test ')") == formatted_error(
        "Error at '<': <String> does not implement the greaterThan method.", 1
    )
    assert run_source("print(1 < 'test')") == formatted_error(
        "Error at ''test'': Expected Int but got String for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(true < true)") == formatted_error(
        "Error at '<': <Bool> does not implement the greaterThan method.", 1
    )
    assert run_source("print(List(2) < List(2))") == formatted_error(
        "Error at '<': <List> does not implement the greaterThan method.", 1
    )
    assert run_source("print(Map(1 -> 'test') < Map(1 -> 'test'))") == formatted_error(
        "Error at '<': <Map> does not implement the greaterThan method.", 1
    )


def test_lesser_equals():
    assert run_source("print(0 <= 1)") == "true"
    assert run_source("print(1 <= 1)") == "true"
    assert run_source("print(2 <= 1)") == "false"
    assert run_source("print(1 <= 1.0)") == formatted_error(
        "Error at '1.0': Expected Int but got Float for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.0 <= 1)") == formatted_error(
        "Error at '1': Expected Float but got Int for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(1.1 <= 1.2)") == "true"
    assert run_source("print(1.2 <= 1.2)") == "true"
    assert run_source("print(1.3 <= 1.2)") == "false"
    assert run_source("print('test' <= 'test ')") == formatted_error(
        "Error at '<=': <String> does not implement the greaterThan method.", 1
    )
    assert run_source("print(1 <= 'test')") == formatted_error(
        "Error at ''test'': Expected Int but got String for parameter other in call to greaterThan.", 1
    )
    assert run_source("print(true <= true)") == formatted_error(
        "Error at '<=': <Bool> does not implement the greaterThan method.", 1
    )
    assert run_source("print(List(2) <= List(2))") == formatted_error(
        "Error at '<=': <List> does not implement the greaterThan method.", 1
    )
    assert run_source("print(Map(1 -> 'test') <= Map(1 -> 'test'))") == formatted_error(
        "Error at '<=': <Map> does not implement the greaterThan method.", 1
    )
