from typing import Iterable
from typing import Optional

from _pytest.python import Function
from _pytest.python import PyCollector


class SpockFunction(Function):
    pass


def generate_spock_functions(
    collector: PyCollector, name: str, obj: object, message: Optional[str]
) -> Iterable[SpockFunction]:
    return []
