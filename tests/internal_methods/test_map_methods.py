from ..main import run_source, formatted_error


def test_toString():
    assert run_source("print(Map().toString())") == "Map()"
    assert run_source("print(Map(1 -> 'test', 2 -> 'test_2').toString())") == "Map(1 -> \"test\", 2 -> \"test_2\")"


def test_init():
    assert run_source("print(Map(1 -> true))") == "Map(1 -> true)"
    assert run_source("print(Map(1 -> 1))") == "Map(1 -> 1)"
    assert run_source("print(Map(1 -> 'test', 2 -> 'test'))") == "Map(1 -> \"test\", 2 -> \"test\")"
    assert run_source("print(Map(1 -> Map(1 -> true)))") == "Map(1 -> Map(1 -> true))"
    assert run_source("print(Map(Map(1 -> true) -> 1))") == "Map(Map(1 -> true) -> 1)"
    assert run_source("print(Map(1))") == formatted_error("Invalid value passed to <Map>.", 1)


def test_equals():
    assert run_source("print(Map(1 -> true).equals(Map(1 -> true)))") == "true"
    assert run_source("print(Map(1 -> false).equals(Map(1 -> true)))") == "false"
    assert run_source("print(Map(2 -> true).equals(Map(1 -> true)))") == "false"
    assert run_source("print(Map(1 -> true).equals(1.0))") == formatted_error("Cannot compare <Map> and <Float>", 1)


def test_is_true():
    assert run_source("print(Map(1 -> true).isTrue())") == "true"
    assert run_source("print(Map().isTrue())") == "false"


def test_add():
    assert run_source("print(Map(1 -> true).add(Map(2 -> true)))") == "Map(1 -> true, 2 -> true)"
    assert run_source("print(Map(1 -> true).add(Map(1 -> false)))") == "Map(1 -> false)"
    assert run_source("print(Map(1 -> true).add(2 -> false))") == "Map(1 -> true, 2 -> false)"
    assert run_source("print(Map(1 -> true).add(true))") == formatted_error("Can only add maps or pairs to maps.", 1)


def test_push():
    assert run_source("""
test = Map(1 -> "test")
test.push(2 -> Map(2 -> "test2"))
print(test)
""") == "Map(1 -> \"test\", 2 -> Map(2 -> \"test2\"))"
    
    assert run_source("""
test = Map(1 -> 'test')
test.push(2 -> 'test2')
print(test)
""") == "Map(1 -> \"test\", 2 -> \"test2\")"
    
    assert run_source("""
test = Map(1 -> 'test')
test.push(2)
print(test)
""") == formatted_error("Invalid value passed to <Map.push>.", 3)


def test_get():
    assert run_source("print(Map(1 -> 'test').get(1))") == "test"
    assert run_source("print(Map(1 -> 'test').get(0))") == formatted_error("Could not find key 0 in <Map>.", 1)


def test_remove():
    assert run_source("print(Map(1 -> 'test').remove(1))") == "Pair(1, \"test\")"
    assert run_source("print(Map().remove(1))") == formatted_error("Could not find key 1 in <Map>.", 1)


def test_iterate():
    assert run_source("print(Map(1 -> 'test', 2 -> 'test2').iterate())") == "<Next>(Pair(1, \"test\"), <Next>(Pair(2, \"test2\"), <Next>(NEXT_SENTINEL, NEXT_SENTINEL)))"
