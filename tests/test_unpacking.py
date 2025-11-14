from .main import run_source, formatted_error


def test_unpack_varargs_to_function():
    assert (
        run_source(
            """
tester: a, b, c {
    print(a)
    print(b)
    print(c)
}

wrapper: varargs values {
    tester(*values)
}

wrapper(1, 2, 3)
        """
        )
        == "1\n2\n3"
    )


def test_unpack_varargs_to_class_init():
    assert (
        run_source(
            """
class Container {
    init: a, b, c {
        return Map("a" -> a, "b" -> b, "c" -> c)
    }
}

wrapper: varargs values {
    container = Container(*values)
    print(container.a)
    print(container.b)
    print(container.c)
}

wrapper(1, 2, 3)
        """
        )
        == "1\n2\n3"
    )


def test_unpack_list_to_function():
    assert (
        run_source(
            """
tester: a, b, c {
    print(a)
    print(b)
    print(c)
}

values = List()
values = values.push(1)
values = values.push(2)
values = values.push(3)

tester(*values)
        """
        )
        == "1\n2\n3"
    )


def test_unpack_custom_iterable():
    assert (
        run_source(
            """
class Wrapper {
    init: varargs values {
        list = List()
        for v in values {
            list = list.push(v)
        }
        return Map("list" -> list)
    }
    
    iterate {
        return self.list.iterate()
    }
}

tester: a, b, c {
    print(a)
    print(b)
    print(c)
}

w = Wrapper(10, 20, 30)
tester(*w)
        """
        )
        == "10\n20\n30"
    )


def test_unpack_with_regular_args():
    assert (
        run_source(
            """
tester: a, b, c, d {
    print(a)
    print(b)
    print(c)
    print(d)
}

wrapper: varargs values {
    tester(1, *values, 4)
}

wrapper(2, 3)
        """
        )
        == "1\n2\n3\n4"
    )


def test_unpack_with_varargs_receiver():
    assert (
        run_source(
            """
tester: varargs values {
    for val in values {
        print(val)
    }
}

wrapper: varargs values {
    tester(*values)
}

wrapper(1, 2, 3)
        """
        )
        == "1\n2\n3"
    )


def test_unpack_non_iterable_error():
    # When unpacking a non-iterable, it's caught at runtime not type-check time
    # The error manifests as passing wrong number of arguments
    assert run_source(
        """
tester: a, b {
    print(a)
}

value = 42
tester(*value)
        """
    ) == formatted_error(
        "Expected between 2 and 2 arguments but got 42.",
        7,
    )


def test_unpack_type_check_not_iterable():
    assert run_source(
        """
tester: a, b {
    print(a)
}

wrapper: value {
    tester(*value)
}

wrapper(42)
        """
    ) == formatted_error(
        "Error at '*': value is not iterable (no iterate method).",
        7,
    )


def test_unpack_nested_in_expression():
    assert (
        run_source(
            """
add: a, b {
    return a + b
}

multiply: a, b {
    return a * b
}

wrapper: varargs values {
    result = add(*values)
    print(result)
}

wrapper(5, 3)
        """
        )
        == "8"
    )


def test_unpack_in_method_call():
    assert (
        run_source(
            """
class Calculator {
    add: a, b {
        return a + b
    }
}

calc = Calculator()
values = List()
values = values.push(10)
values = values.push(20)

result = calc.add(*values)
print(result)
        """
        )
        == "30"
    )


def test_unpack_string_iterable():
    assert (
        run_source(
            """
tester: a, b, c {
    print(a)
    print(b)
    print(c)
}

text = "abc"
tester(*text)
        """
        )
        == "a\nb\nc"
    )


def test_unpack_preserves_iteration_order():
    assert (
        run_source(
            """
tester: varargs values {
    index = 0
    for val in values {
        print(val)
        index = index + 1
    }
}

values = List()
values = values.push("first")
values = values.push("second")
values = values.push("third")

tester(*values)
        """
        )
        == "first\nsecond\nthird"
    )


def test_unpack_in_nested_class_init():
    assert (
        run_source(
            """
class Inner {
    init: a, b {
        return Map("a" -> a, "b" -> b)
    }
}

class Outer {
    init: varargs values {
        return Map("inner" -> Inner(*values))
    }
}

obj = Outer(10, 20)
print(obj.inner.a)
print(obj.inner.b)
        """
        )
        == "10\n20"
    )


def test_unpack_return_value():
    assert (
        run_source(
            """
makeList: varargs dummy {
    list = List()
    list = list.push(1)
    list = list.push(2)
    list = list.push(3)
    return list
}

tester: a, b, c {
    print(a)
    print(b)
    print(c)
}

tester(*makeList())
        """
        )
        == "1\n2\n3"
    )


def test_unpack_with_named_arguments():
    assert (
        run_source(
            """
tester: a, b, c {
    print(a)
    print(b)
    print(c)
}

values = List()
values = values.push(2)
values = values.push(3)

tester(1, *values)
        """
        )
        == "1\n2\n3"
    )


def test_unpack_too_many_regular_args_compile_time():
    assert run_source(
        """
tester: a, b {
    print(a)
    print(b)
}

wrapper: varargs values {
    tester(1, 2, 3, *values)
}

wrapper()
        """
    ) == formatted_error(
        "Error at 'tester': Expected between 2 and 2 arguments in call to tester but got at least 3 (with unpacking).",
        8,
    )


def test_unpack_minimum_args_validation():
    # This should pass type checking because even though we can't determine
    # the exact count, we know there's at least 1 arg (the regular arg)
    # and the function accepts 1-infinity args (varargs)
    assert (
        run_source(
            """
tester: varargs values {
    for val in values {
        print(val)
    }
}

wrapper: varargs values {
    tester(1, *values)
}

wrapper(2, 3)
        """
        )
        == "1\n2\n3"
    )


def test_varargs_type_validation_with_string_method():
    assert (
        run_source(
            """
processor: varargs values {
    for val in values {
        print(val.toUpper())
    }
}

processor("hello", "world")
        """
        )
        == "HELLO\nWORLD"
    )


def test_varargs_type_validation_catches_missing_method():
    assert run_source(
        """
processor: varargs values {
    for val in values {
        print(val.toUpper())
    }
}

processor("hello", 123)
        """
    ) == formatted_error(
        "Error at '123': <class Int> does not have required method 'toUpper'.",
        8,
    )


def test_varargs_validation_catches_all_invalid_args():
    assert run_source(
        """
class NoMethods {
}

processor: varargs values {
    for val in values {
        result = val.add(1)
        print(result)
    }
}

obj1 = NoMethods()
obj2 = NoMethods()
processor(5, obj1, obj2)
        """
    ) == formatted_error(
        "Error at 'obj1': <class NoMethods> does not have required method 'add'.",
        14,
    )


def test_varargs_mixed_regular_and_varargs_type_validation():
    assert (
        run_source(
            """
processor: prefix, varargs values {
    print(prefix.toUpper())
    for val in values {
        print(val.add(10))
    }
}

processor("hello", 5, 15)
        """
        )
        == "HELLO\n15\n25"
    )


def test_varargs_mixed_regular_and_varargs_validation_failure_in_varargs():
    assert run_source(
        """
processor: prefix, varargs values {
    print(prefix.toUpper())
    for val in values {
        print(val.subtract(10))
    }
}

processor("hello", 5, "invalid")
        """
    ) == formatted_error(
        "Error at '5': <class Int> does not have required method 'subtract'.",
        9,
    )


def test_varargs_validation_with_multiple_regular_params():
    assert (
        run_source(
            """
processor: a, b, varargs rest {
    print(a.add(b))
    for val in rest {
        print(val.toUpper())
    }
}

processor(10, 20, "x", "y", "z")
        """
        )
        == "30\nX\nY\nZ"
    )


def test_varargs_validation_failure_with_multiple_regular_params():
    assert run_source(
        """
processor: a, b, varargs rest {
    print(a.add(b))
    for val in rest {
        print(val.toUpper())
    }
}

processor(10, 20, "valid", 123)
        """
    ) == formatted_error(
        "Error at '123': <class Int> does not have required method 'toUpper'.",
        9,
    )


def test_varargs_validation_with_list():
    assert (
        run_source(
            """
processor: varargs values {
    result = values.toString()
    print(result)
}
list = List()
list = list.push(1)
list = list.push(2)
list = list.push(3)
processor(*list)
        """
        )
        == "VarArgs(1, 2, 3)"
    )

    assert (
        run_source(
            """
processor: varargs values {
    for val in values {
        print(val.add(1))
    }
}
list = List()
list = list.push(1)
list = list.push(2)
list = list.push(3)
processor(*list)
        """
        )
        == "2\n3\n4"
    )
