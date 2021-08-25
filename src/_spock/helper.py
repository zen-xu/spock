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
    body = source[source.getstatementrange(0)[1] :].deindent()
    co = compile(str(body), str(filename), "exec")

    eval(co, context)
    context = {k: v for k, v in context.items() if inspect.isfunction(v)}
    for f in context.values():
        f_firstlineno = f.__code__.co_firstlineno + firstlineno
        f.__code__ = f.__code__.replace(co_filename=str(filename), co_firstlineno=f_firstlineno + 1)

    return context
