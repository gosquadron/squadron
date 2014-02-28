from squadron.fileio.singleton import singleton
import pytest

#Simple class
@singleton
class singletest():
    somevar = None
    def update(self, new_val):
        self.somevar = new_val

#Tests constructors affecting it
@singleton
class singletest_extra():
    somevar = None
    def __init__(self):
        #Note that this doesn't affect it!
        self.somevar = None
    
    def update(self, new_val):
        self.somevar = new_val

@pytest.mark.parametrize("class_name", [(singletest), (singletest_extra)])
def test_singleton(class_name):
    new_value = 'something'
    instance_a = class_name()
    assert instance_a.somevar is None
    instance_a.update(new_value)
    assert instance_a.somevar == new_value

    instance_b = class_name()
    assert instance_b.somevar == new_value

    another_val = ':)'
    instance_b.update(another_val)
    assert instance_b.somevar == another_val

    #This is pretty cool now
    assert instance_a.somevar == another_val
