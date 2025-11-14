"""Performance and benchmarking tests for immutable data structures."""

from time import perf_counter
from tests.main import run_source


def test_list_push_performance():
    code = """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            list = list.push(num)
        }
    }
}
print(list.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "1000"
    # 1000 operations should complete in reasonable time
    assert duration < 0.5, f"List push (1000 ops) took {duration:.3f}s, expected < 0.5s"


def test_list_get_performance_after_many_pushes():
    code = """
list = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        list = list.push(num, num, num, num, num)
    }
}
total = 0
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        total = total + 1
    }
}
print(list.length())
print(total)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "510\n100"
    # Access should remain fast even with modification chain
    assert duration < 0.5, (
        f"List operations (500+ pushes) took {duration:.3f}s, expected < 0.5s"
    )


def test_map_push_performance():
    code = """
map = Map()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            map = map.push(((num * 100) + (n * 10) + m) -> "value")
        }
    }
}
print(map.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    # 1000 unique keys (0-999)
    assert result == "1000"
    assert duration < 0.5, f"Map push (1000 ops) took {duration:.3f}s, expected < 3.0s"


def test_map_get_performance():
    code = """
map = Map(0 -> "a", 1 -> "b", 2 -> "c", 3 -> "d", 4 -> "e")
for num in List(5, 6, 7, 8, 9, 10, 11, 12, 13, 14) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        map = map.push((num * 10 + n) -> "value", (num * 10 + n + 1) -> "v2")
    }
}
total = ""
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        val = map.get(0)
    }
}
print(map.length())
print(val)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert "a" in result
    # 200 pushes, 100 gets
    assert duration < 0.5, (
        f"Map operations (200 pushes, 100 gets) took {duration:.3f}s, expected < 0.5s"
    )


def test_object_copy_performance():
    code = """
class Person {
    init: name, age, city, country {
        return Map(
            "name" -> name,
            "age" -> age,
            "city" -> city,
            "country" -> country
        )
    }
}

person = Person("Alice", 30, "NYC", "USA")
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            person = person.age: (person.age + 1)
        }
    }
}
print(person.age)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "1030"
    # 1000 copy operations
    assert duration < 0.5, (
        f"Object copy (1000 ops) took {duration:.3f}s, expected < 3.0s"
    )


def test_nested_copy_performance():
    code = """
class Address {
    init: city {
        return Map("city" -> city)
    }
}

class Person {
    init: name, address {
        return Map("name" -> name, "address" -> address)
    }
}

person = Person("Alice", Address("NYC"))
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            person = person.copy("address.city" -> person.address.city)
        }
    }
}
print(person.address.city)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "NYC"
    # 1000 nested copy operations
    assert duration < 0.5, (
        f"Nested copy (1000 ops) took {duration:.3f}s, expected < 3.0s"
    )


def test_compaction_overhead():
    code = """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            list = list.push(num)
        }
    }
}
print(list.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "1000"
    # Compaction should trigger multiple times but not significantly slow things down
    assert duration < 0.5, (
        f"Compaction overhead (1000 pushes): {duration:.3f}s, expected < 0.5s"
    )


def test_iterator_performance():
    code = """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        list = list.push(num)
    }
}

count = 0
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for item in list {
        count = count + 1
    }
}
print(count)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "1000"
    # Iterating 100 items 10 times = 1000 iterations
    assert duration < 0.5, (
        f"Iterator (1000 iterations) took {duration:.3f}s, expected < 0.5s"
    )


def test_varargs_push_performance():
    code = """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        list = list.push(num, n, num, n, num)
    }
}
print(list.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "500"
    # 100 iterations * 5 items each = 500 items
    assert duration < 0.5, (
        f"Varargs push (500 items) took {duration:.3f}s, expected < 0.5s"
    )


def test_memory_efficiency_with_structural_sharing():
    code = """
list1 = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    list1 = list1.push(num)
}
list2 = list1
for num in List(10, 11, 12, 13, 14, 15, 16, 17, 18, 19) {
    list2 = list2.push(num)
}
list3 = list2
for num in List(20, 21, 22, 23, 24, 25, 26, 27, 28, 29) {
    list3 = list3.push(num)
}
list4 = list3
for num in List(30, 31, 32, 33, 34, 35, 36, 37, 38, 39) {
    list4 = list4.push(num)
}

print(list1.length())
print(list2.length())
print(list3.length())
print(list4.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "10\n20\n30\n40"
    # Should be fast due to structural sharing (40 total pushes)
    assert duration < 0.5, f"Structural sharing test (40 pushes) took {duration:.3f}s"


def test_pop_push_alternating_performance():
    code = """
list = List()
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    list = list.push(num)
}

for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        pair = list.pop()
        list = pair.first
        list = list.push(99)
    }
}

print(list.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "10"
    # 100 pop/push cycles
    assert duration < 0.5, f"Pop/push alternating (100 cycles) took {duration:.3f}s"


def test_large_map_operations():
    code = """
map = Map()
key = 0
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            map = map.push(key -> key)
            key = key + 1
            map = map.push(key -> key)
            key = key + 1
            map = map.push(key -> key)
            key = key + 1
        }
    }
}
print(map.length())
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "3000"
    # 1000 iterations * 3 unique keys = 3000 unique keys
    assert duration < 0.5, f"Large map operations (3000 keys) took {duration:.3f}s"


def test_assignment_expression_performance():
    code = """
class Counter {
    init: value {
        return Map("value" -> value)
    }
}

counter = Counter(0)
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            counter = counter.value: (counter.value + 1)
        }
    }
}
print(counter.value)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "1000"
    # 1000 assignment expression operations
    assert duration < 0.5, f"Assignment expressions (1000 ops) took {duration:.3f}s"


def test_deeply_nested_updates_performance():
    code = """
class City {
    init: name {
        return Map("name" -> name)
    }
}

class Address {
    init: city {
        return Map("city" -> city)
    }
}

class Person {
    init: address {
        return Map("address" -> address)
    }
}

person = Person(Address(City("NYC")))
for num in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
    for n in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
        for m in List(0, 1, 2, 3, 4, 5, 6, 7, 8, 9) {
            person = person.copy("address.city.name" -> "Boston")
        }
    }
}
print(person.address.city.name)
"""
    start = perf_counter()
    result = run_source(code)
    duration = perf_counter() - start

    assert result == "Boston"
    # 1000 deeply nested updates
    assert duration < 0.5, (
        f"Deeply nested updates (1000 ops) took {duration:.3f}s, expected < 3.0s"
    )
