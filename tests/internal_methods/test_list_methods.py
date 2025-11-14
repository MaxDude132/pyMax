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
test = test.push(List(2))
print(test)
""")
        == "List(1, List(2))"
    )
    assert (
        run_source("""
test = List(1)
test = test.push(true)
print(test)
""")
        == "List(1, true)"
    )


def test_pop():
    assert run_source("print(List().pop())") == formatted_error(
        "No more items in <List>.", 1
    )
    # pop() now returns Pair(new_list, value)
    assert (
        run_source("""
result = List(1).pop()
print(result.second)
""")
        == "1"
    )


def test_get():
    assert run_source("print(List(1).get(0))") == "1"
    assert run_source("print(List(1).get(1))") == formatted_error(
        "1 is not a valid index.", 1
    )


def test_extend():
    assert (
        run_source("""
test = List(1)
test = test.extend(List(2))
print(test)
""")
        == "List(1, 2)"
    )
    assert run_source("""
test = List(1)
test = test.extend(true)
print(test)
""") == formatted_error(
        "Error at 'true': Expected List but got Bool for parameter other in call to extend.",
        3,
    )


def test_iterate():
    assert run_source("print(List(1, 2).iterate())") == "<ListIterator>"


def test_list_varargs_push():
    assert (
        run_source(
            """
list = List()
list = list.push(1, 2, 3, 4, 5)
print(list)
        """
        )
        == "List(1, 2, 3, 4, 5)"
    )


def test_method_chaining_lists():
    assert (
        run_source(
            """
list = List().push(1).push(2).push(3)
print(list)
        """
        )
        == "List(1, 2, 3)"
    )


def test_list_extend_immutability():
    assert (
        run_source(
            """
list1 = List(1, 2, 3)
list2 = List(4, 5, 6)
list3 = list1.extend(list2)

print(list1)
print(list3)
        """
        )
        == "List(1, 2, 3)\nList(1, 2, 3, 4, 5, 6)"
    )


def test_list_pop_returns_pair():
    assert (
        run_source(
            """
list = List(1, 2, 3)
result = list.pop()

print(result.first)
print(result.second)
print(list)
        """
        )
        == "List(1, 2)\n3\nList(1, 2, 3)"
    )


def test_structural_sharing_independence():
    assert (
        run_source(
            """
original = List(1, 2, 3)
modified1 = original.push(4)
modified2 = original.push(5)

print(original)
print(modified1)
print(modified2)
        """
        )
        == "List(1, 2, 3)\nList(1, 2, 3, 4)\nList(1, 2, 3, 5)"
    )


def test_length():
    assert run_source("print(List().length())") == "0"
    assert run_source("print(List(1).length())") == "1"
    assert run_source("print(List(1, 2, 3).length())") == "3"
    assert run_source("print(List(1, 2, 3, 4, 5).length())") == "5"


def test_length_after_push():
    assert (
        run_source(
            """
list = List(1, 2, 3)
print(list.length())
list = list.push(4)
print(list.length())
        """
        )
        == "3\n4"
    )


def test_length_after_pop():
    assert (
        run_source(
            """
list = List(1, 2, 3)
print(list.length())
result = list.pop()
new_list = result.first
print(new_list.length())
        """
        )
        == "3\n2"
    )


def test_length_nested_access():
    assert (
        run_source(
            """
class Container {
    init: values {
        return Map("items" -> values)
    }
}

container = Container(List(10, 20, 30))
print(container.items.length())
        """
        )
        == "3"
    )
