from __future__ import annotations

import operator as op

from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from .exceptions import UnableEvalParams


class Parameter:
    def __init__(self, name: str) -> None:
        self.__name__ = name
        self.__param_arguments__: List[Any] = []
        self.__accept_expression__: bool = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__name__})"

    __str__ = __repr__

    def __call__(self, **kwargs: Any) -> Any:
        return kwargs[self.__name__]

    def __build_expression__(self, func: Callable, rv: Optional[Any] = None) -> Expression:
        if not self.__accept_expression__:
            raise BuildExpressionError("only support build expression in table")

        def new_func(**kwargs: Any) -> Any:
            arg = kwargs[self.__name__]
            args = [arg]

            nonlocal rv
            if rv is not None:
                if isinstance(rv, (Parameter, Expression)):
                    rv = rv(**kwargs)
                args.append(rv)
            return func(*args)

        return Expression(new_func)

    def __rrshift__(self, args: Iterable) -> Parameter:
        if not isinstance(args, Iterable):
            raise AddArgumentsFailed("args mut be iterable")
        self.__param_arguments__ += list(args)
        return self

    def __pos__(self) -> Expression:
        return self.__build_expression__(op.pos)

    def __neg__(self) -> Expression:
        return self.__build_expression__(op.neg)

    def __invert__(self) -> Expression:
        return self.__build_expression__(op.invert)

    def __add__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.add, rv)

    def __sub__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.sub, rv)

    def __mul__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.mul, rv)

    def __floordiv__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.floordiv, rv)

    def __truediv__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.truediv, rv)

    def __mod__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.mod, rv)

    def __pow__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.pow, rv)

    def __lshift__(self, rv: Any) -> Union[Parameter, Expression]:
        if self.__accept_expression__:
            return self.__build_expression__(op.lshift, rv)

        if not isinstance(rv, Iterable):
            raise AddArgumentsFailed("args mut be iterable")
        self.__param_arguments__ += list(rv)
        return self

    def __rshift__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.rshift, rv)

    def __and__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.and_, rv)

    def __xor__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.xor, rv)

    def __or__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.or_, rv)

    def __matmul__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.matmul, rv)  # pragma: no cover

    def __lt__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.lt, rv)

    def __le__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.le, rv)

    def __gt__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.gt, rv)

    def __ge__(self, rv: Any) -> Expression:
        return self.__build_expression__(op.ge, rv)

    def __eq__(self, rv: Any) -> Expression:  # type: ignore
        return self.__build_expression__(op.eq, rv)

    def __ne__(self, rv: Any) -> Expression:  # type: ignore
        return self.__build_expression__(op.ne, rv)


class Expression:
    def __init__(self, func: Callable) -> None:
        self.__func__ = func

    def __rebuild_expression__(self, func: Callable, rv: Optional[Any] = None) -> Expression:
        self_func = self.__func__

        if rv is None:

            def new_func(**kwargs: Any) -> Any:
                value = self_func(**kwargs)
                return func(value)

        else:

            if isinstance(rv, Expression):

                def new_func(**kwargs: Any) -> Any:
                    self_value = self_func(**kwargs)
                    rv_value = rv(**kwargs)  # type: ignore
                    return func(self_value, rv_value)

            else:

                def new_func(**kwargs: Any) -> Any:
                    self_value = self_func(**kwargs)
                    return func(self_value, rv)

        return Expression(new_func)

    def __call__(self, **kwargs: Any) -> Any:
        return self.__func__(**kwargs)

    def __pos__(self) -> Expression:
        return self.__rebuild_expression__(op.pos)

    def __neg__(self) -> Expression:
        return self.__rebuild_expression__(op.neg)

    def __invert__(self) -> Expression:
        return self.__rebuild_expression__(op.invert)

    def __add__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.add, rv)

    def __sub__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.sub, rv)

    def __mul__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.mul, rv)

    def __floordiv__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.floordiv, rv)

    def __truediv__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.truediv, rv)

    def __mod__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.mod, rv)

    def __pow__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.pow, rv)

    def __lshift__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.lshift, rv)

    def __rshift__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.rshift, rv)

    def __and__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.and_, rv)

    def __xor__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.xor, rv)

    def __or__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.or_, rv)

    def __matmul__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.matmul, rv)  # pragma: no cover

    def __lt__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.lt, rv)

    def __le__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.le, rv)

    def __gt__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.gt, rv)

    def __ge__(self, rv: Any) -> Expression:
        return self.__rebuild_expression__(op.ge, rv)

    def __eq__(self, rv: Any) -> Expression:  # type: ignore
        return self.__rebuild_expression__(op.eq, rv)

    def __ne__(self, rv: Any) -> Expression:  # type: ignore
        return self.__rebuild_expression__(op.ne, rv)


def declare(*param_names: str) -> Tuple[Parameter, ...]:
    return tuple(Parameter(name) for name in param_names)


class BuildExpressionError(Exception):
    """build expression failed"""


class AddArgumentsFailed(Exception):
    """add arguments failed"""


def zip_parameters_values(*params: Parameter) -> List[Dict[str, Any]]:
    max_len = max(len(param.__param_arguments__) for param in params)
    result = []
    for i in range(max_len):
        arg = {}
        for param in params:
            try:
                arg[param.__name__] = param.__param_arguments__[i]
            except IndexError:
                arg[param.__name__] = None
        result.append(arg)

    return result


def eval_params(**args: Any) -> Dict[str, Any]:
    expression_or_params = {}
    normal_args = {}

    for key, value in args.items():
        if isinstance(value, (Expression, Parameter)):
            expression_or_params[key] = value
        else:
            normal_args[key] = value

    max_recursion_depth = 20
    current_recursion_depth = 0
    while expression_or_params:
        tmp_expression_or_params = dict(**expression_or_params)
        for key, f in tmp_expression_or_params.items():
            try:
                normal_args[key] = f(**normal_args)
                expression_or_params.pop(key)
            except (TypeError, KeyError):
                current_recursion_depth += 1
                if current_recursion_depth == max_recursion_depth:
                    raise UnableEvalParams

    return normal_args
