import pytest

from _pytest.config import Config
from _pytest.python import PyCollector
from _spock.spock import generate_spock_functions


@pytest.hookimpl
def pytest_configure(config: Config):
    config.addinivalue_line("markers", "spock(msg): this marker means use spock test framework")


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector: PyCollector, name: str, obj: object):
    spock_marks = [mark for mark in getattr(obj, "pytestmark", []) if mark.name == "spock"]
    if spock_marks:
        mark = spock_marks[0]
        if mark.args:
            message = mark.args[0]
        else:
            message = None
        return list(generate_spock_functions(collector, name, obj, message))
    return None
