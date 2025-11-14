from .main import run_source, formatted_error


def test_varargs():
    assert (
        run_source(
            """
tester: varargs values {
    print(values)
}
tester("test", "other_test")
        """
        )
        == 'VarArgs("test", "other_test")'
    )


def test_varargs_from_other_varargs():
    assert (
        run_source(
            """
class Tester {
    init: varargs value {
        return Map("value" -> value)
    }
    toString {
        return self.value
    }
}

tester = Tester("test", "other_test")
print(tester.value)
        """
        )
        == 'VarArgs("test", "other_test")'
    )


def test_varargs_cannot_be_created_by_user():
    assert run_source(
        """
test = VarArgs("test", "other_test")
print(test)
        """
    ) == formatted_error("Error at 'VarArgs': Undefined variable 'VarArgs'.", 2)


def test_varargs_type_is_handled():
    assert run_source(
        """
class Tester {
    init: varargs value {
        return Map("value" -> value.toUpper())
    }
    toString {
        return self.value
    }
}

tester = Tester("test", 1)
print(tester.value)
        """
    ) == formatted_error(
        "Error at '1': <class Int> does not have required method 'toUpper'.",
        11,
    )
