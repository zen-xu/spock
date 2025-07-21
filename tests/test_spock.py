from _spock.exceptions import UnableEvalParams
from _spock.spock import generate_arguments


def test_generate_arguments_with_table_style_func():
    def values(_, a, b):
        _ | a | b
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
        _ | a | b
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
                _ | a | b
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
                    _ | a | b
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


def test_spock_missing_where_block(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock
        def test_spock():
            def expect():
                assert 1 == 1
        """
    )

    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=1)


def test_spock_missing_expect_block(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock
        def test_spock():
            def where(filename):
                filename << ["a", "b"]
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(failed=2)


def test_table_params_eval_failed(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock("{a} <= {b}")
        def test_spock():

            def expect(a, b):
                assert a <= b

            def where(_, a, b):
                _ | a | b
                _ | 1 | b
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(errors=1)
    assert (
        pytester.inline_genitems()[0][0]._request.node.name
        == "test_spock[unable to eval 0 params]"
    )


def test_given_block(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock
        def test_spock():
            def given(me):
                me.a = 1
                me.b = 2

            def expect(a, b):
                assert a < b
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=1)


def test_given_block_with_fixture(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock
        def test_spock():
            def given(me, tmpdir):
                me.a = 1
                me.b = 2
                me.working_dir = tmpdir / "working"
                me.working_dir.mkdir()

            def expect(a, b, working_dir):
                assert a < b

                assert working_dir.exists()
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=1)


def test_cleanup_block(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.spock
        def test_spock():
            def given(me, tmpdir):
                me.working_dir = tmpdir

            def expect():
                pass

            def cleanup(working_dir):
                working_dir.remove()
        """
    )
    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=1)


def test_when_and_then_blocks(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.fixture
        def data():
            return "1234"

        @pytest.mark.spock
        def test_zero_division_error():
            def when():
                1 / 0

            def then(excinfo):
                assert excinfo.type == ZeroDivisionError

        @pytest.mark.spock
        def test_raise_runtime_error():
            def when():
                raise ValueError("something wrong")

            def then(excinfo):
                assert excinfo.match("something wrong")

        @pytest.mark.spock
        def test_append_data():
            def given(me):
                me.container = []

            def when(container):
                container.append(1)

            def then(container):
                assert container == [1]

        @pytest.mark.spock
        def test_fixture():
            def when(tmpdir, data):
                (tmpdir / "a.txt").write(data)

            def then(tmpdir, data):
                assert (tmpdir / "a.txt").read() == data

        @pytest.mark.spock
        def test_missing_then_block():
            def when():
                1 + 1
        """
    )

    result = pytester.runpytest("-p", "no:cov", "-p", "no:sugar")
    result.assert_outcomes(passed=4, failed=1)
