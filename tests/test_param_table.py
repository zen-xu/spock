import pytest

from _spock.param_table import ParamTable
from _spock.parameter import Parameter


@pytest.fixture(scope="function")
def table():
    return ParamTable()


@pytest.fixture(scope="function")
def a():
    return Parameter("a")


@pytest.fixture(scope="function")
def b():
    return Parameter("b")


@pytest.fixture(scope="function")
def c():
    return Parameter("c")


class TestParamTable:
    def test_declare_header(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b / c
        assert table.columns[-1] == ["a", "b", "c"]

    def test_add_args(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b / c
        table | 1 | 2 | 3
        table | 4 | 5 | 6

        assert table.arguments_mapping["a"] == [1, 4]
        assert table.arguments_mapping["b"] == [2, 5]
        assert table.arguments_mapping["c"] == [3, 6]

        assert list(table) == [(1, 2, 3), (4, 5, 6)]

    def test_declare_header_in_multi_sections(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b  # section 1
        table | 1 | 2
        table | 4 | 5
        table / c  # section 2
        table | 3
        table | 6

        assert table.arguments_mapping["a"] == [1, 4]
        assert table.arguments_mapping["b"] == [2, 5]
        assert table.arguments_mapping["c"] == [3, 6]

        assert list(table) == [(1, 2, 3), (4, 5, 6)]

    def test_args_section1_has_more_args(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b  # section 1
        table | 1 | 2
        table | 4 | 5
        table / c  # section 2
        table | 3

        assert list(table) == [(1, 2, 3), (4, 5, None)]

    def test_args_section1_has_less_args(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b  # section 1
        table | 1 | 2
        table | 4 | 5
        table / c  # section 2
        table | 3
        table | 6
        table | 7

        assert list(table) == [(1, 2, 3), (4, 5, 6), (None, None, 7)]
