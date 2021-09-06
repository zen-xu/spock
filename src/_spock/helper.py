import ast
import inspect
import sys

from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from _pytest._code.code import Code
from _pytest._code.source import Source


LESS_PY38 = sys.version_info <= (3, 8)


def get_functions_in_function(
    func: Callable,
) -> Dict[str, Callable]:
    """Return functions contained in the passed function."""
    context: Dict[str, Any] = getattr(func, "__globals__", {})

    code = Code.from_function(func)
    args = code.getargs()
    if inspect.ismethod(func):
        context[args[0]] = func.__self__  # type: ignore[attr-defined]

    filename, firstlineno = code.path, code.firstlineno
    source = code.source()
    # skip def statement
    body_statement_lineno = 0
    while True:
        statement = source.getstatement(body_statement_lineno).deindent()
        if any(("def " in line for line in statement.lines)):  # see deepsource PTC-W0016
            body_statement_lineno += len(statement.lines)
            break
        body_statement_lineno += 1

    body_firstlineno = body_statement_lineno
    body = source[body_statement_lineno:].deindent()
    co = compile(str(body), str(filename), "exec")

    eval(co, context)  # skipcq: PYL-W0123
    context = {k: v for k, v in context.items() if inspect.isfunction(v) and k in get_function_names(str(body))}
    for f in context.values():
        f_firstlineno = f.__code__.co_firstlineno + firstlineno
        if LESS_PY38:
            from types import CodeType

            f.__code__ = CodeType(
                f.__code__.co_argcount,
                f.__code__.co_kwonlyargcount,
                f.__code__.co_nlocals,
                f.__code__.co_stacksize,
                f.__code__.co_flags,
                f.__code__.co_code,
                f.__code__.co_consts,
                f.__code__.co_names,
                f.__code__.co_varnames,
                str(filename),  # type: ignore
                f.__code__.co_name,
                f_firstlineno + body_firstlineno,
                f.__code__.co_lnotab,
                f.__code__.co_freevars,
                f.__code__.co_cellvars,
            )
        else:
            f.__code__ = f.__code__.replace(co_filename=str(filename), co_firstlineno=f_firstlineno + body_firstlineno)

    return context


def get_function_names(source: str) -> List[str]:
    source = Source(source).deindent()  # type: ignore
    bodies = ast.parse(str(source)).body
    return [body.name for body in bodies if isinstance(body, ast.FunctionDef)]


class Box:
    _data: Dict[str, Any]

    def __new__(cls) -> "Box":
        box = super().__new__(cls)
        box._data = {}

        return box

    def __setattr__(self, name: str, value: Any) -> None:
        if not name.startswith("_"):
            self._data[name] = value
        super().__setattr__(name, value)
