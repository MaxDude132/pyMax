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
    init: String arg {
        self.arg = arg
    }
}
test = Test("test")
print(test.arg)
"""
        )
        == "test"
    )


def test_get_attribute_on_class():
    assert (
        run_source(
            """
class Test {
    init: String arg {
        self.arg = arg
    }
}
print(Test.arg)
"""
        )
        == formatted_error("Only instances have properties.", 7)
    )
