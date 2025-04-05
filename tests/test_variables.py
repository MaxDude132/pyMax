from .main import run_source, formatted_error


def test_set_variable():
    assert run_source("""
test = "test"
print(test)
""") == "test"
    

def test_inexistant_variable():
    assert run_source("""
print(test)
""") == formatted_error("Undefined variable 'test'.", 2)