from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(List().toString())") == "List()"
    assert run_source("print(List(1,2,3).toString())") == "List(1, 2, 3)"


def test_init():
    assert run_source("print(List(true))") == "List(true)"
    assert run_source("print(List(1))") == "List(1)"
    assert run_source("print(List(List(1)))") == "List(List(1))"
    assert run_source("print(List(1,2))") == "List(1, 2)"


def test_equals():
    assert run_source("print(List(1).equals(List(1)))") == "true"
    assert run_source("print(List(1).equals(List(2)))") == "false"
    assert run_source("print(List(1).equals(1.0))") == formatted_error(
        "Error at '1.0': Expected List but got Float for parameter other in call to equals.",
        1,
    )


def test_toBool():
    assert run_source("print(List(1).toBool())") == "true"
    assert run_source("print(List().toBool())") == "false"


def test_add():
    assert run_source("print(List(1).add(List(2)))") == "List(1, 2)"
    assert run_source("print(List(1).add(true))") == formatted_error(
        "Error at 'true': Expected List but got Bool for parameter other in call to add.",
        1,
    )


def test_push():
    assert (
        run_source("""
test = List(1)
test.push(List(2))
print(test)
""")
        == "List(1, List(2))"
    )
    assert (
        run_source("""
test = List(1)
test.push(true)
print(test)
""")
        == "List(1, true)"
    )


def test_pop():
    assert run_source("print(List().pop())") == formatted_error(
        "No more items in <List>.", 1
    )
    assert run_source("print(List(1).pop())") == "1"


def test_get():
    assert run_source("print(List(1).get(0))") == "1"
    assert run_source("print(List(1).get(1))") == formatted_error(
        "1 is not a valid index.", 1
    )


def test_extend():
    assert (
        run_source("""
test = List(1)
test.extend(List(2))
print(test)
""")
        == "List(1, 2)"
    )
    assert run_source("""
test = List(1)
test.extend(true)
print(test)
""") == formatted_error(
        "Error at 'true': Expected List but got Bool for parameter other in call to extend.",
        3,
    )


def test_iterate():
    assert run_source("print(List(1, 2).iterate())") == "<ListIterator>"
