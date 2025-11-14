from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(Map().toString())") == "Map()"
    assert (
        run_source("print(Map(1 -> 'test', 2 -> 'test_2').toString())")
        == 'Map(1 -> "test", 2 -> "test_2")'
    )


def test_init():
    assert run_source("print(Map(1 -> true))") == "Map(1 -> true)"
    assert run_source("print(Map(1 -> 1))") == "Map(1 -> 1)"
    assert (
        run_source("print(Map(1 -> 'test', 2 -> 'test'))")
        == 'Map(1 -> "test", 2 -> "test")'
    )
    assert run_source("print(Map(1 -> Map(1 -> true)))") == "Map(1 -> Map(1 -> true))"
    assert run_source("print(Map(Map(1 -> true) -> 1))") == "Map(Map(1 -> true) -> 1)"
    assert run_source("print(Map(1))") == formatted_error(
        "Error at '1': Expected Pair but got Int for parameter items in call to Map.", 1
    )


def test_equals():
    assert run_source("print(Map(1 -> true).equals(Map(1 -> true)))") == "true"
    assert run_source("print(Map(1 -> false).equals(Map(1 -> true)))") == "false"
    assert run_source("print(Map(2 -> true).equals(Map(1 -> true)))") == "false"
    assert run_source("print(Map(1 -> true).equals(1.0))") == formatted_error(
        "Error at '1.0': Expected Map but got Float for parameter other in call to equals.",
        1,
    )


def test_toBool():
    assert run_source("print(Map(1 -> true).toBool())") == "true"
    assert run_source("print(Map().toBool())") == "false"


def test_add():
    assert (
        run_source("print(Map(1 -> true).add(Map(2 -> true)))")
        == "Map(1 -> true, 2 -> true)"
    )
    assert run_source("print(Map(1 -> true).add(Map(1 -> false)))") == "Map(1 -> false)"
    # assert run_source("print(Map(1 -> true).add(2 -> false))") == "Map(1 -> true, 2 -> false)"
    assert run_source("print(Map(1 -> true).add(true))") == formatted_error(
        "Error at 'true': Expected Map or Pair but got Bool for parameter key in call to add.",
        1,
    )


def test_push():
    assert (
        run_source("""
test = Map(1 -> "test")
test = test.push(2 -> Map(2 -> "test2"))
print(test)
""")
        == 'Map(1 -> "test", 2 -> Map(2 -> "test2"))'
    )

    assert (
        run_source("""
test = Map(1 -> 'test')
test = test.push(2 -> 'test2')
print(test)
""")
        == 'Map(1 -> "test", 2 -> "test2")'
    )

    assert run_source("""
test = Map(1 -> 'test')
test = test.push(2)
print(test)
""") == formatted_error(
        "Error at '2': Expected Pair but got Int for parameter items in call to push.",
        3,
    )


def test_get():
    assert run_source("print(Map(1 -> 'test').get(1))") == "test"
    assert run_source("print(Map(1 -> 'test').get(0))") == formatted_error(
        "Could not find key 0 in <Map>.", 1
    )


def test_remove():
    # remove() now returns Pair(new_map, removed_value)
    assert (
        run_source("""
result = Map(1 -> 'test').remove(1)
print(result.second)
""")
        == "test"
    )
    assert run_source("print(Map().remove(1))") == formatted_error(
        "Could not find key 1 in <Map>.", 1
    )


def test_iterate():
    assert (
        run_source("print(Map(1 -> 'test', 2 -> 'test2').iterate())") == "<MapIterator>"
    )


def test_map_varargs_push():
    assert (
        run_source(
            """
map = Map()
map = map.push(1 -> "one", 2 -> "two", 3 -> "three")
print(map.get(1))
print(map.get(2))
print(map.get(3))
        """
        )
        == "one\ntwo\nthree"
    )


def test_method_chaining_maps():
    assert (
        run_source(
            """
map = Map().push(1 -> "a").push(2 -> "b").push(3 -> "c")
print(map.get(2))
        """
        )
        == "b"
    )


def test_map_remove_returns_pair():
    assert (
        run_source(
            """
map = Map(1 -> "one", 2 -> "two")
result = map.remove(1)

print(result.second)
print(map.get(1))
        """
        )
        == "one\none"
    )


def test_length():
    assert run_source("print(Map().length())") == "0"
    assert run_source("print(Map(1 -> 'a').length())") == "1"
    assert run_source("print(Map(1 -> 'a', 2 -> 'b', 3 -> 'c').length())") == "3"


def test_length_after_push():
    assert (
        run_source(
            """
map = Map(1 -> "a", 2 -> "b")
print(map.length())
map = map.push(3 -> "c")
print(map.length())
        """
        )
        == "2\n3"
    )


def test_length_after_remove():
    assert (
        run_source(
            """
map = Map(1 -> "a", 2 -> "b", 3 -> "c")
print(map.length())
result = map.remove(2)
new_map = result.first
print(new_map.length())
        """
        )
        == "3\n2"
    )


def test_length_nested_access():
    assert (
        run_source(
            """
class Container {
    init: data {
        return Map("storage" -> data)
    }
}

container = Container(Map(1 -> "x", 2 -> "y"))
print(container.storage.length())
        """
        )
        == "2"
    )
