from _spock.exceptions import UnableEvalParams
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


def test_spock_function_with_where_block(pytester):

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock("{a} <= {b}")
        def test_spock():

            def expect(a, b):
                assert a <= b

            def where(_, a, b):
                _ / a / b
                _ | 1 | 2
                _ | 3 | 4
                _ | 7 | 6
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=2, failed=1)


def test_spock_method_with_where_block(pytester):

    pytester.makepyfile(
        """
        import pytest

        class TestSpock:
            @pytest.mark.spock("{a} <= {b}")
            def test_spock(self):

                def expect(a, b):
                    assert a <= b

                def where(_, a, b):
                    _ / a / b
                    _ | 1 | 2
                    _ | 3 | 4
                    _ | 7 | 6
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=2, failed=1)


def test_spock_function_with_fixture(pytester):

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock
        def test_spock():
            def expect(tmpdir, filename):
                new_dir = tmpdir / filename

            def where(filename):
                filename << ["a", "b"]
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=2)
