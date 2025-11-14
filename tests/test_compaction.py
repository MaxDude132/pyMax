from tests.main import run_source


def test_list_auto_compaction_on_threshold():
    result = run_source(
        """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14) {
    list = list.push(num)
}
print(list.length())
    """
    )
    assert result == "15"


def test_list_compaction_preserves_values():
    result = run_source(
        """
list = List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
print(list.get(0))
print(list.get(5))
print(list.get(10))
print(list.get(15))
print(list.get(19))
    """
    )
    assert result == "0\n5\n10\n15\n19"


def test_map_auto_compaction_on_threshold():
    result = run_source(
        """
map = Map()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14) {
    map = map.push(num -> num)
}
print(map.length())
    """
    )
    assert result == "15"


def test_map_compaction_preserves_values():
    result = run_source(
        """
map = Map(0 -> 0, 1 -> 2, 2 -> 4, 3 -> 6, 4 -> 8)
map = map.push(5 -> 10, 6 -> 12, 7 -> 14, 8 -> 16, 9 -> 18)
map = map.push(10 -> 20, 11 -> 22, 12 -> 24, 13 -> 26, 14 -> 28)
print(map.length())
print(map.get(0))
print(map.get(7))
print(map.get(14))
    """
    )
    assert result == "15\n0\n14\n28"


def test_list_deep_chain_with_modifications():
    result = run_source(
        """
list = List(1, 2, 3, 4, 5)
list = list.push(10, 11, 12, 13, 14)
list = list.push(15, 16, 17, 18, 19)
list = list.push(20, 21, 22, 23, 24)
list = list.push(25, 26, 27, 28, 29)
print(list.length())
print(list.get(0))
print(list.get(24))
    """
    )
    assert result == "25\n1\n29"


def test_map_deep_chain_with_modifications():
    result = run_source(
        """
map = Map(1 -> "one", 2 -> "two")
map = map.push(10 -> "v", 11 -> "v", 12 -> "v", 13 -> "v")
map = map.push(14 -> "v", 15 -> "v", 16 -> "v", 17 -> "v")
map = map.push(18 -> "v", 19 -> "v", 20 -> "v", 21 -> "v")
map = map.push(22 -> "v", 23 -> "v", 24 -> "v", 25 -> "v")
map = map.push(26 -> "v", 27 -> "v", 28 -> "v", 29 -> "v")
print(map.length())
print(map.get(1))
    """
    )
    assert result == "22\none"


def test_list_mixed_operations_before_compaction():
    result = run_source(
        """
list = List(1, 2, 3)
list = list.push(0, 10, 20, 30, 40, 50, 60, 70)
list = list.set(0, 999)
print(list.get(0))
print(list.length())
    """
    )
    assert result == "999\n11"


def test_map_mixed_operations_before_compaction():
    result = run_source(
        """
map = Map(1 -> "a", 2 -> "b", 3 -> "c")
map = map.push(10 -> "v", 11 -> "v", 12 -> "v", 13 -> "v")
map = map.push(14 -> "v", 15 -> "v", 16 -> "v", 17 -> "v")
pair = map.remove(2)
new_map = pair.first
print(new_map.length())
print(new_map.get(1))
    """
    )
    assert result == "10\na"


def test_list_compaction_after_pop():
    result = run_source(
        """
list = List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
list = list.push(10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
list = list.push(20, 21, 22, 23, 24)
pair = list.pop()
new_list = pair.first
pair2 = new_list.pop()
final_list = pair2.first
print(final_list.length())
print(final_list.get(22))
    """
    )
    assert result == "23\n22"


def test_list_immutability_after_compaction():
    result = run_source(
        """
list1 = List(1, 2, 3)
list2 = list1
list2 = list2.push(10, 11, 12, 13, 14)
list2 = list2.push(15, 16, 17, 18, 19)
list2 = list2.push(20, 21, 22, 23, 24)
print(list1.length())
print(list2.length())
print(list1.get(0))
    """
    )
    assert result == "3\n18\n1"


def test_map_immutability_after_compaction():
    result = run_source(
        """
map1 = Map(1 -> "a", 2 -> "b")
map2 = map1
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14) {
    map2 = map2.push(num + 10 -> "value")
}
print(map1.length())
print(map2.length())
    """
    )
    assert result == "2\n17"


def test_list_nested_in_object_compaction():
    result = run_source(
        """
class Container {
    init: items {
        return Map("items" -> items)
    }
}

container = Container(List())
container = container.items: container.items.push(0, 1, 2, 3, 4)
container = container.items: container.items.push(5, 6, 7, 8, 9)
container = container.items: container.items.push(10, 11, 12, 13, 14)
container = container.items: container.items.push(15, 16, 17, 18, 19)
print(container.items.length())
    """
    )
    assert result == "20"


def test_map_nested_in_object_compaction():
    result = run_source(
        """
class Config {
    init: settings {
        return Map("settings" -> settings)
    }
}

config = Config(Map())
config = config.settings: config.settings.push(0 -> 0, 1 -> 1, 2 -> 2, 3 -> 3, 4 -> 4)
config = config.settings: config.settings.push(5 -> 5, 6 -> 6, 7 -> 7, 8 -> 8, 9 -> 9)
config = config.settings: config.settings.push(10 -> 10, 11 -> 11, 12 -> 12, 13 -> 13, 14 -> 14)
config = config.settings: config.settings.push(15 -> 15, 16 -> 16, 17 -> 17, 18 -> 18, 19 -> 19)
print(config.settings.length())
    """
    )
    assert result == "20"


def test_list_compaction_threshold_config():
    result = run_source(
        """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10) {
    list = list.push(num)
}
print(list.length())
    """
    )
    assert result == "11"


def test_varargs_push_with_compaction():
    result = run_source(
        """
list = List()
list = list.push(1, 2, 3, 4, 5)
list = list.push(6, 7, 8, 9, 10)
list = list.push(11, 12, 13, 14, 15)
print(list.length())
print(list.get(0))
print(list.get(14))
    """
    )
    assert result == "15\n1\n15"
