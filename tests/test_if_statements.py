from .main import run_source, formatted_error


def test_if_equal():
    assert run_source(
        """
test = "test"

if test == "test" {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_not_equal():
    assert run_source(
        """
test = "tes"

if test != "test" {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_non_empty_string():
    assert run_source(
        """
test = "test"

if test {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_empty_string():
    assert run_source(
        """
test = ""

if !test {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_non_zero_int():
    assert run_source(
        """
test = 1

if test {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_zero_int():
    assert run_source(
        """
test = 0

if !test {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_non_zero_float():
    assert run_source(
        """
test = 1.1

if test {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_zero_float():
    assert run_source(
        """
test = 0.0

if !test {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_else():
    assert run_source(
        """
test = 0.0

if test {
    print("it did not work...")
} else {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_else_if():
    assert run_source(
        """
test = 0.0

if test == 1.0 {
    print("it did not work...")
} else if test == 0.0 {
    print("it worked!")
}
        """
) == "it worked!"
    

def test_if_ternary():
    assert run_source(
        """
test = 0.0

value = if test == 1.0 {
    "it did not work..."
} else if test == 0.0 {
    "it worked!"
} else {
    "it did not work..."
}
print(value)
        """
) == "it worked!"
    

def test_if_ternary_missing_else():
    assert run_source(
        """
test = 0.0

value = if test == 1.0 {
    "it did not work..."
} else if test == 0.0 {
    "it worked!"
}
print(value)
        """
) == formatted_error("Error at 'print': Expect 'else' clause after then branch of if expression.", 9)

    

def test_if_ternary_different_types_on_branches():
    assert run_source(
        """
test = 0.0

value = if test == 1.0 {
    "it did not work..."
} else {
    2
}
print(value)
        """
) == formatted_error("Error at 'if': Got different return types in if expression: String and Int.", 4)
