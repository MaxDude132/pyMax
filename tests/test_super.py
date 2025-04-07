from .main import run_source, formatted_error


def test_super_with_method():
    assert run_source("""
class Test {
    init: String value {
        self.value = value            
    }                
}
                      
class OtherTest: Test {
    init: String value {
        super(value)                  
    }
}
                      
other_test = OtherTest("test")
print(other_test.value)
""") == "test"
    

def test_super_without_superclass():
    assert run_source("""
class Test {
    init: String value {
        super(value)       
    }                
}
                      
test = Test("test")
print(test.value)
""") == formatted_error("Error at 'super': Cannot use 'super' in a class with no superclass.", 4)


def test_super_multiple_inheritance():
    # Skips the first, gets to the second
    assert run_source("""
class First {       
}
                      
class Second {
    init: String value {
        self.value = value                  
    }
}
                      
class Third: First, Second {
    init: String value {
        super(value)                  
    }
}
                      
third = Third("test")
print(third.value)
""") == "test"
    
