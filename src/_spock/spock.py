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
            fixtureinfo=collector.session._fixturemanager,
        )
        return

    argnames = tuple(n for n in Code.from_function(where_block).getargs() if n != "_")
    modulecol = collector.getparent(Module)
    assert modulecol is not None
    module = modulecol.obj
    clscol = collector.getparent(Class)
    cls = clscol and clscol.obj or None
    fm = collector.session._fixturemanager

    definition = FunctionDefinition.from_parent(collector, name=name, callobj=obj)
    metafunc = Metafunc(definition, definition._fixtureinfo, collector.config, cls=cls, module=module)

    for idx, argument in enumerate(generate_arguments(where_block)):
        if isinstance(argument, UnableEvalParams):

            def failed() -> None:
                raise ValueError(f"Unable to eval index {idx} params")

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
            except Exception:
                id = "-".join(map(str, argument.values()))

            id = f"{name}[{id}]"
            fixtureinfo = fixtures.FuncFixtureInfo(
                argnames=argnames,
                initialnames=argnames,
                names_closure=list(argnames),
                name2fixturedefs={
                    k: [
                        fixtures.FixtureDef(
                            fixturemanager=fm,
                            baseid=None,
                            argname=k,
                            params=list(argument.values()),
                            func=fixtures.get_direct_param_fixture_func,
                            scope="function",
                        )
                    ]
                    for k in argnames
                },
            )
            fixtureinfo.prune_dependency_tree()

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
