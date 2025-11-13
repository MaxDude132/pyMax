from .main import run_source, formatted_error


def test_simple_function():
    assert (
        run_source(
            """
test: arg_1 {
    print(arg_1)
}
test("test")
"""
        )
        == "test"
    )


def test_simple_function_arg_passed_by_name():
    assert (
        run_source(
            """
test: arg_1, arg_2 {
    print(arg_1, arg_2)
}
test(arg_2: 3, arg_1: "test")
"""
        )
        == "test 3"
    )


def test_inexistant_function():
    assert run_source(
        """
test("test")
"""
    ) == formatted_error("Error at 'test': Undefined variable 'test'.", 2)


def test_recursive_function():
    assert (
        run_source(
            """
test: arg_1, passes {
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


def test_recursive_function_with_return_type():
    assert (
        run_source(
            """
test: arg_1, passes {
    if passes != 0 {
        arg = arg_1 + passes.toString()
        return test(arg, passes - 1)
    }
    return arg_1
}

test_ret = test("test", 3)
print(test_ret)
"""
        )
        == "test321"
    )


def test_missing_arguments():
    assert run_source(
        """
test: arg_1 {
    print(arg_1)
}
test()
"""
    ) == formatted_error(
        "Error at 'test': Expected between 1 and 1 arguments in call to test but got 0.",
        5,
    )


def test_wrong_number_of_arguments():
    assert run_source(
        """
test: arg_1, arg_2 {
    print(arg_1, arg_2)
}
test("test")
"""
    ) == formatted_error(
        "Error at 'test': Expected between 2 and 2 arguments in call to test but got 1.",
        5,
    )


def test_arguments_with_default():
    assert (
        run_source(
            """
test: arg_1 = "test" {
    print(arg_1)
}
test()
"""
        )
        == "test"
    )

    assert run_source(
        """
test: arg_1 = "test", arg_2 {
    print(arg_1)
}
"""
    ) == formatted_error(
        "Error at 'arg_2': Cannot set a parameter without a default value after a parameter with a default value.",
        2,
    )


def test_function_with_multiple_return_types_hidden_in_if_statement():
    assert run_source(
        """
test: arg_1 {
    if arg_1 == "test" {
        return arg_1
    } else {
        return 2
    }
}

t = test("test")
print(t)
"""
    ) == formatted_error(
        "Error at 'test': Multiple return types found for function.",
        2,
    )


def test_function_with_multiple_return_types_based_on_argument_call():
    assert run_source(
        """
test: arg_1 {
    if arg_1 == 3 {
        return arg_1.toString()
    } else {
        return 2
    }
}

t = test(3)
print(t)
"""
    ) == formatted_error(
        "Error at 'test': Multiple return types found for function.",
        2,
    )


def test_function_with_multiple_return_types_based_on_chained_argument_call():
    assert run_source(
        """
test: arg_1 {
    if arg_1 == 3 {
        return arg_1.add(1).toString()
    } else {
        return 2
    }
}

t = test(3)
print(t)
"""
    ) == formatted_error(
        "Error at 'test': Multiple return types found for function.",
        2,
    )


def test_function_with_return_in_if_statement():
    assert run_source(
        """
test: arg_1 {
    if arg_1 == "test" {
        fake = 2
        2
        -- Noise just to ensure that only the return counts for typing
        return arg_1
    } else {
        return "else"
    }
}

t = 2
t = test("test")
print(t)
"""
    ) == formatted_error(
        "Error at 't': Cannot redefine variable of type <class Int> to type <class String>.",
        14,
    )
