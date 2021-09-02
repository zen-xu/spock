from _spock.spock import UnableEvalParams
from _spock.spock import generate_arguments


def test_generate_arguments_with_table_style_func():
    def values(_, a, b):
        _ / a / b
        _ | 1 | 2
        _ | 3 | 4

    assert generate_arguments(values) == [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
    ]


def test_generate_arguments_with_pipe_style_func():
    def values(a, b):
        a << [1, 3]
        b << [2, 4]

    assert generate_arguments(values) == [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
    ]


def test_generate_arguments_with_table_style_failed():
    def values(_, a, b):
        _ / a / b
        _ | 1 | b
        _ | 3 | 4

    results = generate_arguments(values)
    assert isinstance(results[0], UnableEvalParams)
    assert results[1] == {"a": 3, "b": 4}
