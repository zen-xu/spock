import inspect

from typing import Any
from typing import Callable
from typing import Dict

from _pytest._code.code import Code


def get_functions_in_function(
    func: Callable,
) -> Dict[str, Callable]:
    """Return functions contained in the passed function."""
    context: Dict[str, Any] = {}

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
        if str(statement).startswith("def "):
            break
        body_statement_lineno += 1

    body_firstlineno = source.getstatementrange(body_statement_lineno)[1]
    body = source[body_firstlineno:].deindent()
    co = compile(str(body), str(filename), "exec")

    eval(co, context)  # skipcq: PYL-W0123
    context = {k: v for k, v in context.items() if inspect.isfunction(v)}
    for f in context.values():
        f_firstlineno = f.__code__.co_firstlineno + firstlineno
        f.__code__ = f.__code__.replace(co_filename=str(filename), co_firstlineno=f_firstlineno + body_firstlineno)

    return context
