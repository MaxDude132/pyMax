from tests.main import run_source


def test_simple_field_update():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }
}

person = Person("Alice", 30)
person2 = person.age: 31
print(person.age)
print(person2.age)
        """
        )
        == "30\n31"
    )


def test_assignment_expression_returns_new_instance():
    assert (
        run_source(
            """
class Person {
    init: name {
        return Map("name" -> name)
    }
}

person1 = Person("Alice")
person2 = person1.name: "Bob"
print(person1.name)
print(person2.name)
        """
        )
        == "Alice\nBob"
    )


def test_assignment_expression_chaining():
    assert (
        run_source(
            """
class Person {
    init: name, age, city {
        return Map("name" -> name, "age" -> age, "city" -> city)
    }
}

person = Person("Alice", 30, "NYC")
updated = person.age: 31
updated = updated.city: "Boston"
print(person.age)
print(person.city)
print(updated.age)
print(updated.city)
        """
        )
        == "30\nNYC\n31\nBoston"
    )


def test_assignment_expression_with_nested_objects():
    assert (
        run_source(
            """
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
new_address = person.address.city: "Boston"
person2 = person.address: new_address
print(person.address.city)
print(person2.address.city)
        """
        )
        == "NYC\nBoston"
    )


def test_assignment_expression_with_numbers():
    assert (
        run_source(
            """
class Counter {
    init: count {
        return Map("count" -> count)
    }
}

counter = Counter(0)
counter = counter.count: 1
counter = counter.count: (counter.count + 1)
print(counter.count)
        """
        )
        == "2"
    )


def test_assignment_expression_with_strings():
    assert (
        run_source(
            """
class Config {
    init: setting {
        return Map("setting" -> setting)
    }
}

config = Config("default")
config = config.setting: "custom"
print(config.setting)
        """
        )
        == "custom"
    )


def test_assignment_expression_with_booleans():
    assert (
        run_source(
            """
class Flag {
    init: enabled {
        return Map("enabled" -> enabled)
    }
}

flag = Flag(false)
flag = flag.enabled: true
if flag.enabled {
    print("enabled")
}
        """
        )
        == "enabled"
    )


def test_assignment_expression_with_lists():
    assert (
        run_source(
            """
class Container {
    init: items {
        return Map("items" -> items)
    }
}

container = Container(List(1, 2, 3))
new_items = container.items.push(4)
container = container.items: new_items
print(container.items.length())
        """
        )
        == "4"
    )


def test_assignment_expression_preserves_other_fields():
    assert (
        run_source(
            """
class Person {
    init: name, age, city {
        return Map("name" -> name, "age" -> age, "city" -> city)
    }
}

person = Person("Alice", 30, "NYC")
person2 = person.age: 31
print(person2.name)
print(person2.age)
print(person2.city)
        """
        )
        == "Alice\n31\nNYC"
    )


def test_assignment_expression_in_loop():
    assert (
        run_source(
            """
class Counter {
    init: value {
        return Map("value" -> value)
    }
}

counter = Counter(0)
for i in List(1, 2, 3, 4, 5) {
    counter = counter.value: (counter.value + 1)
}
print(counter.value)
        """
        )
        == "5"
    )


def test_assignment_expression_with_method_call():
    assert (
        run_source(
            """
class Person {
    init: name {
        return Map("name" -> name)
    }
    
    getName {
        return self.name
    }
}

person = Person("Alice")
person2 = person.name: person.getName()
print(person2.name)
        """
        )
        == "Alice"
    )


def test_assignment_expression_error_on_undefined_field():
    result = run_source(
        """
class Person {
    init: name {
        return Map("name" -> name)
    }
}

person = Person("Alice")
person2 = person.age: 30
    """
    )
    assert "Cannot modify undefined field" in result or "age" in result


def test_assignment_expression_vs_copy():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }
}

person = Person("Alice", 30)
person_via_expr = person.age: 31
person_via_copy = person.copy("age" -> 31)
print(person_via_expr.age)
print(person_via_copy.age)
        """
        )
        == "31\n31"
    )


def test_multiple_assignment_expressions_in_sequence():
    assert (
        run_source(
            """
class Point {
    init: x, y {
        return Map("x" -> x, "y" -> y)
    }
}

point = Point(0, 0)
point = point.x: 10
point = point.y: 20
print(point.x)
print(point.y)
        """
        )
        == "10\n20"
    )


def test_assignment_expression_with_expression_value():
    assert (
        run_source(
            """
class Calculator {
    init: result {
        return Map("result" -> result)
    }
}

calc = Calculator(0)
calc = calc.result: (10 + 5 * 2)
print(calc.result)
        """
        )
        == "20"
    )


def test_assignment_expression_immutability():
    assert (
        run_source(
            """
class Box {
    init: value {
        return Map("value" -> value)
    }
}

box1 = Box(100)
box2 = box1.value: 200
box3 = box1.value: 300
print(box1.value)
print(box2.value)
print(box3.value)
        """
        )
        == "100\n200\n300"
    )
