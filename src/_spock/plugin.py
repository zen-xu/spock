import pytest

from _pytest.config import Config

from .spock import generate_spock_functions


@pytest.hookimpl
def pytest_configure(config: Config):
    config.addinivalue_line("markers", "spock(msg): this marker means use spock test framework")


# @pytest.mark.tryfirst
# def pytest_pycollect_makeitem(collector: PyCollector, name: str, obj: object):
#     spock_marks = [mark.name for mark in obj.pytestmark if mark.name == "spock"]
#     if spock_marks:
#         mark = spock_marks[0]
#         if mark.args:
#             message = mark.args[0]
#         else:
#             message = None
#         return list(generate_spock_functions(collector, name, obj, message))
#     else:
#         return []


@pytest.mark.try_first
def pytest_collection_modifyitems(config: Config, items):
    tmp_items = []
    for item in items:

        marker = item.get_closest_marker("spock")
        if marker:
            if marker.args:
                message = marker.args[0]
            else:
                message = None
            tmp_items += list(generate_spock_functions(config, item, message))
        else:
            tmp_items.append(item)

    items[:] = tmp_items
