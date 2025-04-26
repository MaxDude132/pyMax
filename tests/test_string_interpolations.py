from .main import run_source, formatted_error


def test_string_interpolation():
    assert run_source(
        """
name = "world"
print("Hello ${name}!")
        """
) == "Hello world!"


def test_string_interpolation_with_depth():
    assert run_source(
        """
name = "world"
print("Hello ${"my ${name}"}!")
        """
) == "Hello my world!"


def test_string_interpolation_escaped():
    assert run_source(
        """
name = "world"
print("Hello \${name}!")
        """
) == "Hello ${name}!"
