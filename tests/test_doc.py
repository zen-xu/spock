import pytest


@pytest.mark.spock("maximum of {a} and {b} is {c}")
def test_maximum():
    def expect(a, b, c):
        assert max(a, b) == c

    def where(_, a, b, c):
        _ | a | b | c
        _ | 3 | 7 | 7
        _ | 5 | 4 | 5
        _ | 9 | 9 | 9


@pytest.mark.spock("{a} > {b}")
def test_bigger():
    def expect(a, b):
        assert a > b

    def where(_, a, b):
        _ | a | b
        _ | 7 | 3
        _ | 5 | 2


@pytest.mark.spock
def test_append_element():
    def given(me):
        me.stack = []
        me.elem = 1

    def when(stack, elem):
        # stimulus
        stack.append(elem)

    def then(stack, elem):
        # response
        assert len(stack) == 1
        assert stack.pop() == elem


@pytest.mark.spock
def test_zero_division():
    def when():
        1 / 0

    def then(excinfo):
        assert excinfo.type is ZeroDivisionError


@pytest.mark.spock
def test_maximum2():
    def given(me):
        me.x = max(1, 2)

    def then(x):
        assert x == 2


@pytest.mark.spock
def test_file():
    def given(me, tmpdir):
        me.file = open(tmpdir / "test.txt", "w+")

    def when(file):
        file.write("hello")

    def then(file):
        file.seek(0)
        assert file.read() == "hello"

    def cleanup(file):
        file.close()


@pytest.mark.spock("max({a}, {b}) == {c}")
def test_maximum_of_two_numbers():
    def expect(a, b, c):
        assert max(a, b) == c

    def where(a, b, c):
        a << [5, 3]
        b << [1, 9]
        c << [5, 9]


@pytest.mark.spock("max({a}, {b}) == {c}")
def test_maximum_of_two_numbers_table_style():
    def expect(a, b, c):
        assert max(a, b) == c

    def where(_, a, b, c):
        _ | a | b | c
        _ | 5 | 1 | 5
        _ | 3 | 9 | 9


@pytest.mark.spock("max({a}, {b}) == {c}")
def test_maximum_of_two_numbers_table_multi_parts_style():
    def expect(a, b, c):
        assert max(a, b) == c

    def where(_, a, b, c):
        _ | a | b
        _ | 5 | 1
        _ | 3 | 9

        _ | c
        _ | 5
        _ | 9
