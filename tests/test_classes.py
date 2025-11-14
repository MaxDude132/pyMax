from .main import run_source, formatted_error


def test_create_class():
    assert (
        run_source(
            """
class Test {
}
print(Test)
"""
        )
        == "<class Test>"
    )


def test_class_init():
    assert (
        run_source(
            """
class Test {
    init: arg {
        return Map("arg" -> arg)
    }
}
test = Test("test")
print(test.arg)
"""
        )
        == "test"
    )


def test_get_attribute_on_class():
    assert run_source(
        """
class Test {
    init: arg {
        return Map("arg" -> arg)
    }
}
print(Test.arg)
"""
    ) == formatted_error("Only instances have properties.", 7)


def test_class_copy_with_pairs():
    assert (
        run_source(
            """
class Person {
    init: name, age, city {
        return Map("name" -> name, "age" -> age, "city" -> city)
    }
}

person1 = Person("Alice", 30, "NYC")
person2 = person1.copy("age" -> 31, "city" -> "Boston")

print(person1.name)
print(person1.age)
print(person1.city)
print(person2.name)
print(person2.age)
print(person2.city)
        """
        )
        == "Alice\n30\nNYC\nAlice\n31\nBoston"
    )


def test_copy_single_field():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }
}

person = Person("Alice", 30)
person = person.copy("age" -> 31)
print(person.age)
        """
        )
        == "31"
    )


def test_copy_validates_field_names():
    assert run_source(
        """
class Person {
    init: name {
        return Map("name" -> name)
    }
}

person = Person("Alice")
person = person.copy("invalid" -> "value")
        """
    ).startswith("[line") and "Cannot modify undefined field 'invalid'" in run_source(
        """
class Person {
    init: name {
        return Map("name" -> name)
    }
}

person = Person("Alice")
person = person.copy("invalid" -> "value")
        """
    )


def test_nested_class_with_list():
    assert (
        run_source(
            """
class Container {
    init: varargs items {
        list = List()
        for item in items {
            list = list.push(item)
        }
        return Map("items" -> list)
    }
    
    add: item {
        new_items = self.items.push(item)
        return self.copy("items" -> new_items)
    }
}

c1 = Container(1, 2, 3)
c2 = c1.add(4)

print(c1.items)
print(c2.items)
        """
        )
        == "List(1, 2, 3)\nList(1, 2, 3, 4)"
    )


def test_class_copy_structural_sharing():
    assert (
        run_source(
            """
class Person {
    init: name, age, hobbies {
        return Map("name" -> name, "age" -> age, "hobbies" -> hobbies)
    }
}

hobbies = List("reading", "coding")
person1 = Person("Alice", 30, hobbies)
person2 = person1.copy("age" -> 31)

print(person1.hobbies)
print(person2.hobbies)
print(person1.age)
print(person2.age)
        """
        )
        == 'List("reading", "coding")\nList("reading", "coding")\n30\n31'
    )


def test_copy_nested_field_updates():
    assert (
        run_source(
            """
class Address {
    init: city, zip {
        return Map("city" -> city, "zip" -> zip)
    }
}

class Person {
    init: name, address {
        return Map("name" -> name, "address" -> address)
    }
}

person = Person("Alice", Address("NYC", "10001"))
updated = person.copy("address.city" -> "Boston")
print(updated.address.city)
print(updated.address.zip)
print(person.address.city)
        """
        )
        == "Boston\n10001\nNYC"
    )


def test_copy_deeply_nested_updates():
    assert (
        run_source(
            """
class City {
    init: name, zip {
        return Map("name" -> name, "zip" -> zip)
    }
}

class Address {
    init: street, city {
        return Map("street" -> street, "city" -> city)
    }
}

class Person {
    init: name, address {
        return Map("name" -> name, "address" -> address)
    }
}

person = Person("Alice", Address("123 Main", City("NYC", "10001")))
updated = person.copy("address.city.name" -> "Boston")
print(updated.address.city.name)
print(updated.address.city.zip)
print(person.address.city.name)
        """
        )
        == "Boston\n10001\nNYC"
    )


def test_copy_multiple_nested_updates():
    assert (
        run_source(
            """
class Address {
    init: city, zip {
        return Map("city" -> city, "zip" -> zip)
    }
}

class Person {
    init: name, address, age {
        return Map("name" -> name, "address" -> address, "age" -> age)
    }
}

person = Person("Alice", Address("NYC", "10001"), 30)
updated = person.copy("address.city" -> "Boston", "address.zip" -> "02101", "age" -> 31)
print(updated.address.city)
print(updated.address.zip)
print(updated.age)
print(person.address.city)
print(person.age)
        """
        )
        == "Boston\n02101\n31\nNYC\n30"
    )


def test_field_update_syntax():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }
}

person1 = Person("Alice", 30)
person2 = person1.age: 31
print(person1.age)
print(person2.age)
        """
        )
        == "30\n31"
    )


def test_field_update_preserves_other_fields():
    assert (
        run_source(
            """
class Person {
    init: name, age, city {
        return Map("name" -> name, "age" -> age, "city" -> city)
    }
}

person1 = Person("Alice", 30, "NYC")
person2 = person1.age: 31
print(person1.name)
print(person2.name)
print(person1.age)
print(person2.age)
        """
        )
        == "Alice\nAlice\n30\n31"
    )


def test_field_update_chaining():
    assert (
        run_source(
            """
class Person {
    init: name, age, city {
        return Map("name" -> name, "age" -> age, "city" -> city)
    }
}

person = Person("Alice", 30, "NYC").age: 31
person = person.city: "Boston"
print(person.age)
print(person.city)
        """
        )
        == "31\nBoston"
    )


def test_dynamic_field_access_with_variable():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }
}

person = Person("Alice", 30)
fieldName = "age"
updated = person.copy(fieldName -> 31)
print(updated.age)
        """
        )
        == "31"
    )


def test_dynamic_field_access_with_expression():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }
}

person = Person("Alice", 30)
updated = person.copy(("a" + "ge") -> 31)
print(updated.age)
        """
        )
        == "31"
    )


def test_dynamic_nested_field_access():
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
path = "address.city"
updated = person.copy(path -> "Boston")
print(updated.address.city)
        """
        )
        == "Boston"
    )


def test_field_access_works_properly():
    assert (
        run_source(
            """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }

    mangled_name {
        return self.name + "_mangled"
    }
}

person = Person("Alice", 30)
print(person.name)
print(person.age)
print(person.mangled_name)
print(person.mangled_name())
"""
        )
        == "Alice\n30\n<method mangled_name of <instanceof Person>>\nAlice_mangled"
    )


def test_field_access_errors():
    assert run_source(
        """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }

    mangled_name {
        return self.name + "_mangled"
    }
}

person = Person("Alice", 30)
print(person.inexistent)
"""
    ) == formatted_error(
        "Error at 'inexistent': Attribute inexistent not found for class Person.", 13
    )

    assert run_source(
        """
class Person {
    init: name, age {
        return Map("name" -> name, "age" -> age)
    }

    mangled_name {
        return self.name + "_mangled"
    }
}

person = Person("Alice", 30)
print(person.inexistent())
"""
    ) == formatted_error(
        "Error at 'inexistent': Attribute inexistent not found for class Person.", 13
    )
