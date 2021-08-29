import pytest


@pytest.mark.spock("{a} < {b}")
def test_spock():
    def expect(a, b):
        assert a > b

    def where(a, b):
        a << [1, 2]
        b << [3, 4]
