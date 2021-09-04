from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from _pytest import fixtures
from _pytest._code.code import Code
from _pytest.python import CallSpec2
from _pytest.python import Class
from _pytest.python import Function
from _pytest.python import FunctionDefinition
from _pytest.python import Metafunc
from _pytest.python import Module
from _pytest.python import PyCollector

from .exceptions import UnableEvalParams
from .helper import get_functions_in_function
from .param_table import ParamTable
from .parameter import Parameter
from .parameter import eval_params
from .parameter import zip_parameters_values


class SpockFunction(Function):
    def setup(self) -> None:
        super().setup()

        testfunc = self.obj
        blocks = get_functions_in_function(testfunc)
        for block_name in ["given", "when", "then", "expect", "cleanup"]:
            block_func = blocks.get(block_name)
            if block_func is None:
                continue
            block_args = Code.from_function(block_func).getargs()
            for arg in block_args:
                if arg not in self.funcargs:
                    self.funcargs[arg] = self._request.getfixturevalue(arg)

    def runtest(self) -> None:
        testfunc = self.obj
        blocks = get_functions_in_function(testfunc)
        expect_block = blocks["expect"]
        expect_argnames = Code.from_function(expect_block).getargs()
        funcargs = self.funcargs
        testargs = {arg: funcargs[arg] for arg in expect_argnames}
        expect_block(**testargs)


def generate_spock_functions(
    collector: PyCollector, name: str, obj: object, message: Optional[str]
) -> Iterable[SpockFunction]:
    blocks = get_functions_in_function(obj)  # type: ignore
    where_block = blocks.get("where")
    if where_block is None:
        yield SpockFunction.from_parent(
            collector,
            name=name,
            callobj=obj,
        )
        return

    argnames = tuple(n for n in Code.from_function(where_block).getargs() if n != "_")
    module_col = collector.getparent(Module)
    if module_col is None:
        raise ValueError("module can't be None")  # pragma: no cover
    module = module_col.obj
    cls_col = collector.getparent(Class)
    cls = cls_col.obj if cls_col else None
    fm = collector.session._fixturemanager

    definition = FunctionDefinition.from_parent(collector, name=name, callobj=obj)
    metafunc = Metafunc(definition, definition._fixtureinfo, collector.config, cls=cls, module=module)

    for idx, argument in enumerate(generate_arguments(where_block)):
        if isinstance(argument, UnableEvalParams):

            def failed(idx: int = idx) -> None:

                raise ValueError(f"Unable to eval index {idx} params")  # pragma: no cover

            id = f"{name}[unable to eval {idx} params]"
            yield SpockFunction.from_parent(
                collector,
                name=id,
                callobj=failed,
                keywords={id: True},
                originalname=name,
            )
        else:
            try:
                id = message.format(**argument)  # type: ignore
            except (AttributeError, KeyError):
                id = "-".join(map(str, argument.values()))

            id = f"{name}[{id}]"
            fixtureinfo = fixtures.FuncFixtureInfo(
                argnames=argnames,
                initialnames=argnames,
                names_closure=list(argnames),
                name2fixturedefs={
                    argname: [
                        fixtures.FixtureDef(
                            fixturemanager=fm,
                            baseid=name,
                            argname=argname,
                            params=list(argument.values()),
                            func=fixtures.get_direct_param_fixture_func,
                            scope="function",
                        )
                    ]
                    for argname in argnames
                },
            )

            callspec = CallSpec2(metafunc)
            callspec.setmulti2(
                {k: "params" for k in argnames},
                argnames,
                argument.values(),
                id,
                [],
                4,
                idx,
            )

            yield SpockFunction.from_parent(
                collector,
                name=id,
                callspec=callspec,
                callobj=obj,
                fixtureinfo=fixtureinfo,
                keywords={id: True},
                originalname=name,
            )


def generate_arguments(func: Callable) -> List[Union[Dict[str, Any], UnableEvalParams]]:
    code = Code.from_function(func)
    arg_names = code.getargs()

    if "_" not in arg_names:
        params = {arg: Parameter(arg) for arg in arg_names}
        func(**params)
        return zip_parameters_values(*params.values())  # type: ignore
    params = {arg: Parameter(arg) for arg in {*arg_names} - {"_"}}
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
