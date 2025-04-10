from .main import run_source, formatted_error


def test_type_check_user_defined_function():
    assert (
        run_source(
            """
test: String param1, Int param2 {
    print(param1, param2)
}

test("test", param2: 2)
            """
        )
    ) == "test 2"


def test_type_check_user_defined_function_wrong_type():
    assert (
        run_source(
            """
test: String param1, Int param2 {
    print(param1, param2)
}

test("test", param2: "test2")
            """
        )
    ) == formatted_error("Error at '\"test2\"': Expected Int but got String for parameter param2 in call to test.", 6)


def test_type_check_user_defined_function_with_variable():
    assert (
        run_source(
            """
test: String param1, Int param2 {
    print(param1, param2)
}

test_param_1 = "test"
test(test_param_1, param2: 2)
            """
        )
    ) == "test 2"


def test_type_check_user_defined_function_with_variable_wrong_type():
    assert (
        run_source(
            """
test: String param1, Int param2 {
    print(param1, param2)
}

test_param_1 = 2
test(test_param_1, param2: 2)
            """
        )
    ) == formatted_error("Error at 'test_param_1': Expected String but got Int for parameter param1 in call to test.", 7)


def test_type_check_user_defined_function_with_user_defined_type():
    assert (
        run_source(
            """
class Tester {
    init: String test {
        self.test = test
    }
}

test: Tester param1, Tester param2 {
    print(param1.test, param2.test)
}

tester = Tester("test")
other_tester = Tester("test2")

test(tester, param2: other_tester)
            """
        )
    ) == "test test2"


def test_type_check_user_defined_function_with_user_defined_type_wrong_type():
    assert (
        run_source(
            """
class Tester {
    init: String test {
        self.test = test
    }
}

test: Tester param1, Tester param2 {
    print(param1.test, param2.test)
}

tester = Tester("test")
other_tester = "test2"

test(tester, param2: other_tester)
            """
        )
    ) == formatted_error("Error at 'other_tester': Expected Tester but got String for parameter param2 in call to test.", 15)


def test_type_check_works_with_superclasses():
    assert (
        run_source(
            """
class Tester {
    init: String test {
        self.test = test
    }
}

class CustomTester: Tester {
    init: String test {
        self.test = test
    }
}

test: Tester param1, Tester param2 {
    print(param1.test, param2.test)
}

tester = Tester("test")
other_tester = CustomTester("test2")

test(tester, param2: other_tester)
            """
        )
    ) == "test test2"


def test_type_check_can_redefine_variable_with_same_type():
    assert (
        run_source(
            """
test = 2
test = 5  -- This should succeed
print(test)
            """
        )
    ) == "5"


def test_type_check_cannot_redefine_variable_type():
    assert (
        run_source(
            """
test = 2
test = "test"  -- This should fail
print(test)
            """
        )
    ) == formatted_error("Error at 'test': Cannot redefine variable of type Int to type String.", 3)


def test_type_check_can_redefine_variables_that_share_superclass():
    assert (
        run_source(
            """
class Shared {}
class Class1: Shared {}
class Class2: Shared {}

test = Class1()
test = Class2()
print(test)
            """
        )
    ) == "<instanceof Class2>"


def test_type_check_cannot_redefine_variables_that_dont_share_superclass():
    assert (
        run_source(
            """
class Shared {}
class Class1: Shared {}
class Class2 {}

test = Class1()
test = Class2()
print(test)
            """
        )
    ) == formatted_error("Error at 'test': Cannot redefine variable of type Class1 to type Class2.", 7)


def test_type_check_redefining_to_superclass_is_taken_into_account():
    assert (
        run_source(
            """
class Shared {}
class Class1: Shared {}
class Class2: Shared {}

class Tester {
    init: Class2 test {
        self.test = test
    }
}

test = Class1()
test = Class2()

new_test = Tester(test)
print(new_test)
            """
        )
    ) == formatted_error("Error at 'test': Expected Class2 but got Shared for parameter test in call to Tester.", 15)


def test_type_check_handles_return():
    assert (
        run_source(
            """
test: String value {
    return value
}

str = test("strtest")
str = 2
            """
        )
    ) == formatted_error("Error at 'str': Cannot redefine variable of type String to type Int.", 7)


def test_type_check_cannot_change_attribute_type():
    assert (
        run_source(
            """
class Tester {
    init: String test {
        self.test = test
        self.test = 2
    }
}

test = Tester("strtest")
            """
        )
    ) == formatted_error("Error at 'test': Cannot redefine attribute of type String to type Int.", 5)
