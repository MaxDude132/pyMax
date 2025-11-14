import pytest
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


@pytest.mark.skip(
    reason="Type checker doesn't track iterator types from built-in collections"
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


@pytest.mark.skip(reason="Custom iterators require Phase 2 immutable iterator support")
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
        value = self.iterable.values.get(index)
        self.index = index + 1
        is_end = index >= self.iterable.values.length - 1
        return Next(value, is_end)
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
