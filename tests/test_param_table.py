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
        assert table.columns[-1] == [a, b, c]

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

    def test_table_to_dict(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b / c
        table | 1 | 2 | 3
        table | 4 | 5 | 6
        table | 7 | 8 | 9

        assert table.to_dict() == [
            {"a": 1, "b": 2, "c": 3},
            {"a": 4, "b": 5, "c": 6},
            {"a": 7, "b": 8, "c": 9},
        ]

    def test_table_to_dict_with_params(self, table: ParamTable, a: Parameter, b: Parameter, c: Parameter):
        table / a / b
        table | 1 | a + 1
        table | b | 5
        table | 7 | 8

        table / c
        table | 3
        table | 6
        table | a + 2

        assert table.to_dict() == [
            {"a": 1, "b": a + 1, "c": 3},
            {"a": b, "b": 5, "c": 6},
            {"a": 7, "b": 8, "c": a + 2},
        ]
