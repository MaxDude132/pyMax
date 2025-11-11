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
        self.values = List()
        for value in values {
            self.values.push(value)
        }
    }
}

test = CustomIterable(1, 2, 3)

for number in test {
    print(number)
}
        """
    ) == formatted_error(
        "Error at 'for': Cannot iterate over instance of <class CustomIterable> that does not implement 'iterate'.",
        13,
    )


def test_for_loop_on_user_defined_class_defining_iterate():
    assert (
        run_source(
            """
class CustomIterable {
    init: varargs values {
        self.values = List()
        for value in values {
            self.values.push(value)
        }
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
        self.values = List()

        for val in values {
            self.values.push(val)
        }
    }
}


class CustomIterator {
    init: iterable {
        self.iterable = iterable
        self.index = 0
    }

    next {
        is_end = false
        index = self.index
        self.index = index + 1
        return Next(self.iterable.values.get(index), is_end)
    }
}


class CustomIterable {
    init: varargs values {
        self.values = CustomContainer(values)
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
