from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from _pytest._code.code import Code
from _pytest.config import Config
from _pytest.python import Function

from .exceptions import UnableEvalParams
from .helper import get_functions_in_function
from .param_table import ParamTable
from .parameter import Parameter
from .parameter import eval_params
from .parameter import zip_parameters_values


class SpockFunction(Function):
    ...


def generate_spock_functions(config: Config, func: Function, message: Optional[str]) -> Iterable[SpockFunction]:
    __traceback__ = None  # noqa: F841

    blocks = get_functions_in_function(func.obj)

    arguments = []
    where_block = blocks.get("where")
    if where_block:
        arguments = generate_arguments(where_block)

    expect_block = blocks.get("expect")
    if not arguments:
        yield SpockFunction.from_parent(func.parent, name=func.name, callobj=expect_block)
        return

    # definition = FunctionDefinition.from_parent(func.parent, name="expect", callobj=expect_block)
    # fixtureinfo = definition._fixtureinfo

    # clscol = func.getparent(Class)
    # cls = clscol and clscol.obj or None
    # modulecol = func.getparent(Module)

    # metafunc = Metafunc(
    #     definition=definition,
    #     fixtureinfo=fixtureinfo,
    #     config=config,
    #     cls=cls,
    #     module=modulecol.obj,  # type: ignore
    # )
    # callspec = CallSpec2(metafunc)

    for idx, argument in enumerate(arguments):
        if isinstance(argument, UnableEvalParams):

            def raise_error() -> None:
                raise UnableEvalParams

            yield SpockFunction.from_parent(
                func.parent, name=f"unable eval params for {idx}", callobj=raise_error, originalname=func.name
            )
        else:
            if message:
                name = message.format(**argument)
            else:
                name = "-".join(argument.values())

            # newcallspec = callspec.copy()
            # argnames = argument.keys()
            # newcallspec.setmulti2(
            #     valtypes={k: "funcargs" for k in argnames},
            #     argnames=list(argnames),
            #     valset=argument.values(),
            #     id=name,
            #     marks=[],
            #     scopenum=4,
            #     param_index=idx,
            # )

            # breakpoint()
            # callobj = pytest.mark.parametrize(list(argument.keys()), [(*argument.values(),)])(expect_block)

            yield SpockFunction.from_parent(
                func.parent,
                name=name,
                callobj=expect_block,
                originalname=func.name,
            )


def generate_arguments(func: Callable) -> List[Union[Dict[str, Any], UnableEvalParams]]:
    code = Code.from_function(func)
    arg_names = code.getargs()

    if "_" not in arg_names:
        params = {arg: Parameter(arg) for arg in arg_names}
        func(**params)
        return zip_parameters_values(*params.values())  # type: ignore
    else:
        params = {arg: Parameter(arg) for arg in set(arg_names) - set(["_"])}
        table = ParamTable()
        params["_"] = table  # type: ignore
        func(**params)
        args = table.to_dict()
        result: List[Union[Dict[str, Any], UnableEvalParams]] = []
        for arg in args:
            try:
                result.append(eval_params(**arg))
            except UnableEvalParams as e:
                result.append(e)
        return result
