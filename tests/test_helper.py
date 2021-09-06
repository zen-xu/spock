import pytest

from _spock.helper import get_function_names
from _spock.helper import get_functions_in_function


def func1():
    def a():
        return 1

    data = 4

    def b():
        return data

    def c():
        raise ValueError()


def test_get_functions_in_function():
    funcs = get_functions_in_function(func1)
    assert list(funcs.keys()) == ["a", "b", "c"]

    assert funcs["a"]() == 1
    assert funcs["b"]() == 4
    with pytest.raises(ValueError):
        funcs["c"]()

    assert funcs["a"].__code__.co_firstlineno == func1.__code__.co_firstlineno + 1
    assert funcs["a"].__code__.co_filename == __file__


class Class:
    data1 = 2
    data2 = [4, 5]

    def a(self):
        def func():
            return 1 + self.data1

    @classmethod
    def b(
        cls,
        a,
        b,
        c,
    ):
        def func():
            return [3] + cls.data2

    @staticmethod
    def c():
        def func():
            return "abc"


def test_get_functions_in_method():
    obj = Class()
    funcs = get_functions_in_function(obj.a)
    assert funcs["func"]() == 1 + obj.data1
    assert funcs["func"].__code__.co_firstlineno == 38
    assert funcs["func"].__code__.co_filename == __file__


def test_get_functions_in_classmethod():
    funcs = get_functions_in_function(Class.b)
    assert funcs["func"]() == [3] + Class.data2
    assert funcs["func"].__code__.co_firstlineno == 48
    assert funcs["func"].__code__.co_filename == __file__


def test_get_functions_in_staticmethod():
    funcs = get_functions_in_function(Class.c)
    assert funcs["func"]() == "abc"
    assert funcs["func"].__code__.co_firstlineno == 53
    assert funcs["func"].__code__.co_filename == __file__


def test_no_functions_defined_in_function():
    def func():
        pass

    funcs = get_functions_in_function(func)
    assert funcs == {}


def test_get_function_names():
    code = """
    a = 1
    def hello():
        pass

    def world():
        pass

    class C:
        def inner(self):
            pass

    @abc
    def new():
        pass
    """
    assert get_function_names(code) == ["hello", "world", "new"]


GLOBAL_VAR = "123"


def return_global_var():
    def func():
        return GLOBAL_VAR


def test_handle_global_var1():
    assert get_functions_in_function(return_global_var)["func"]() == "123"


def test_box():
    from _spock.helper import Box

    box = Box()
    box.a = 1
    box.b = "123"
    box._c = 4.5
    assert box._data == {"a": 1, "b": "123"}
    assert box.a == 1  # type: ignore
