from .main import run_source, formatted_error


def test_for_loop_on_list():
    assert (
        run_source(
            """
test = List(1, 2, 3)
for number in test {
    print(number)
}
        """
        )
        == "1\n2\n3"
    )


def test_for_loop_on_map():
    assert (
        run_source(
            """
test = Map(1 -> "test", 2 -> "test2")
for pair in test {
    print(pair)
}
        """
        )
        == 'Pair(1, "test")\nPair(2, "test2")'
    )


def test_for_loop_on_string():
    assert (
        run_source(
            """
test = "123"
for number in test {
    print(number)
}
        """
        )
        == "1\n2\n3"
    )


def test_for_loop_on_int():
    assert (
        run_source(
            """
test = 3
for number in test {
    print(number)
}
        """
        )
        == "0\n1\n2"
    )


def test_for_loop_on_float():
    assert run_source(
        """
test = 3.0
for number in test {
    print(number)
}
        """
    ) == formatted_error(
        "Error at 'for': Cannot iterate over instance of <class Float> that does not implement 'iterate'.",
        3,
    )


def test_for_loop_on_user_defined_class():
    assert run_source(
        """
class CustomIterable {
    init: varargs values {
        list = List()
        for value in values {
            list = list.push(value)
        }
        return Map("values" -> list)
    }
}

test = CustomIterable(1, 2, 3)

for number in test {
    print(number)
}
        """
    ) == formatted_error(
        "Error at 'for': Cannot iterate over instance of <class CustomIterable> that does not implement 'iterate'.",
        14,
    )


def test_for_loop_on_user_defined_class_defining_iterate():
    assert (
        run_source(
            """
class CustomIterable {
    init: varargs values {
        list = List()
        for value in values {
            list = list.push(value)
        }
        return Map("values" -> list)
    }

    iterate {
        return self.values.iterate()
    }
}

test = CustomIterable(1, 2, 3)

for number in test {
    print(number)
}
        """
        )
        == "1\n2\n3"
    )


def test_for_loop_on_user_defined_class_defining_next():
    assert (
        run_source(
            """
class CustomContainer {
    init: varargs values {
        list = List()
        for val in values {
            list = list.push(val)
        }
        return Map("values" -> list)
    }
}


class CustomIterator {
    init: iterable {
        return Map("iterable" -> iterable, "index" -> 0)
    }

    next {
        index = self.index
        if index >= self.iterable.values.length() {
            return null
        }
        value = self.iterable.values.get(index)
        new_iter = self.copy("index" -> (index + 1))
        return value -> new_iter
    }
}


class CustomIterable {
    init: varargs values {
        return Map("values" -> CustomContainer(*values))
    }

    iterate {
        return CustomIterator(self.values)
    }
}

test = CustomIterable(1, 2, 3)

for number in test {
    print(number)
}
        """
        )
        == "1\n2\n3"
    )


def test_user_defined_immutable_iterator():
    assert (
        run_source(
            """
class Range {
    init: start, end {
        return Map("start" -> start, "end" -> end, "current" -> start)
    }
    
    iterate {
        return self
    }
    
    next {
        if self.current >= self.end {
            return null
        }
        value = self.current
        new_range = self.copy("current" -> (self.current + 1))
        return value -> new_range
    }
}

range = Range(0, 3)
for i in range {
    print(i)
}
print(range.current)
        """
        )
        == "0\n1\n2\n0"
    )


def test_type_of_object_in_for_loop():
    assert (
        run_source(
            """
for i in List(1, 2, 3) {
    print(i + 1)
}
        """
        )
        == "2\n3\n4"
    )


def test_illegal_call_on_object_in_for_loop():
    assert run_source(
        """
for i in List(1, 2, 3) {
    print(i.inexistent())
}
        """
    ) == formatted_error(
        "Error at 'i': <class Int> does not have required method 'inexistent'.", 2
    )
