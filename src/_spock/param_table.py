from __future__ import annotations

import itertools

from collections import defaultdict
from itertools import chain
from itertools import cycle
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set

from .parameter import Parameter


class ParamTable(Iterable):
    def __init__(self) -> None:
        self.columns: List[List[Parameter]] = [[]]
        self.arguments_mapping: DefaultDict[str, List[Any]] = defaultdict(list)
        self.current_columns_generate: Optional[cycle[Parameter]] = None
        self.seen_param_names: Set[str] = set()

    def __or__(self, arg: Any) -> ParamTable:
        if isinstance(arg, Parameter) and arg.__name__ not in self.seen_param_names:
            self.seen_param_names.add(arg.__name__)
            if self.current_columns_generate is not None:
                self.current_columns_generate = None
                self.columns.append([])
            self.columns[-1].append(arg)
            return self

        # enable Parameter __accept_expression__
        for column in chain(*self.columns):
            column.__accept_expression__ = True

        if self.current_columns_generate is None:
            self.current_columns_generate = cycle(self.columns[-1])

        column = next(self.current_columns_generate)
        self.arguments_mapping[column.__name__].append(arg)
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
        return [dict(zip((column.__name__ for column in itertools.chain(*self.columns)), row)) for row in self]
