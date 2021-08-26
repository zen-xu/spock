from __future__ import annotations

import itertools

from collections import defaultdict
from itertools import cycle
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional

from .parameter import Parameter


class ParamTable(Iterable):
    def __init__(self) -> None:
        self.columns: List[List[str]] = [[]]
        self.arguments_mapping: DefaultDict[str, List[Any]] = defaultdict(list)
        self.current_columns_generate: Optional[cycle[str]] = None

    def __truediv__(self, param: Parameter) -> ParamTable:
        if self.current_columns_generate is not None:
            self.current_columns_generate = None
            self.columns.append([])

        self.columns[-1].append(param.__name__)
        return self

    def __or__(self, arg: Any) -> ParamTable:
        if self.current_columns_generate is None:
            self.current_columns_generate = cycle(self.columns[-1])

        column_name = next(self.current_columns_generate)
        self.arguments_mapping[column_name].append(arg)
        return self

    def __iter__(self) -> Iterator[Any]:
        max_len = max(len(args) for args in self.arguments_mapping.values())
        for i in range(max_len):
            items = []
            for arguments in self.arguments_mapping.values():
                try:
                    arg = arguments[i]
                except IndexError:
                    arg = None
                items.append(arg)
            yield tuple(items)

    def to_dict(self) -> List[Dict[str, Any]]:
        column_names = list(itertools.chain(*self.columns))
        return [dict(zip(column_names, row)) for row in self]
