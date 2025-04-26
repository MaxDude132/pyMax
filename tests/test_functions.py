from .main import run_source, formatted_error


def test_simple_function():
    assert (
        run_source(
            """
test: String arg_1 {
    print(arg_1)
}
test("test")
"""
        )
        == "test"
    )


def test_inexistant_function():
    assert (
        run_source(
            """
test("test")
"""
        )
        == formatted_error("Error at 'test': Undefined variable 'test'.", 2)
    )


def test_recursive_function():
    assert (
        run_source(
            """
test: String arg_1, Int passes {
    if passes < 3 {
        print(arg_1)
        test(arg_1, passes + 1)
    }
}
test("test", 0)
"""
        )
        == "test\ntest\ntest"
    )


def test_missing_arguments():
    assert (
        run_source(
            """
test: String arg_1 {
    print(arg_1)
}
test()
"""
        )
        == formatted_error("Error at 'test': Expected between 1 and 1 arguments in call to test but got 0.", 5)
    )


def test_wrong_number_of_arguments():
    assert (
        run_source(
            """
test: String arg_1, String arg_2 {
    print(arg_1, arg_2)
}
test("test")
"""
        )
        == formatted_error("Error at 'test': Expected between 2 and 2 arguments in call to test but got 1.", 5)
    )


def test_arguments_with_default():
    assert (
        run_source(
            """
test: String arg_1 = "test" {
    print(arg_1)
}
test()
"""
        )
        == "test"
    )

    assert (
        run_source(
            """
test: String arg_1 = "test", String arg_2 {
    print(arg_1)
}
"""
        )
        == formatted_error(
            "Error at 'arg_2': Cannot set a parameter without a default value after a parameter with a default value.",
            2,
        )
    )
