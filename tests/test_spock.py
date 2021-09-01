import pytest


@pytest.mark.spock("{a} < {b}")
def test_spock():
    def expect(a, b):
        assert a < b

    def where(_, a, b, c):
        # fmt: off
        _ / a / b / c
        _ | 1 | 2 | 3
        _ | 2 | 4 | 4
        # fmt: on


class TestDemo:
    @pytest.mark.spock("1 <= {a} < {b}")
    def test_spock(self):
        def expect(a, b):
            assert 1 <= a < b

        def where(_, a, b, c):
            # fmt: off
            _ / a / b / c
            _ | 1 | 2 | 3
            _ | 2 | 4 | 4
            # fmt: on

    @pytest.mark.spock("{a} > {b}")
    def test_spock2(self):
        def expect(a, b):
            assert a > b

        def where(_, a, b):
            # fmt: off
            _ / a / b
            _ | 1 | 2
            _ | 2 | 4
            # fmt: on
