import pytest


@pytest.mark.spock("{a} < {b}")
def test_spock():
    def expect(a, b):
        assert a < b

    def where(_, a, b):
        _ / a / b
        _ | 1 | 1
        _ | 3 | 4
