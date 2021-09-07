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
