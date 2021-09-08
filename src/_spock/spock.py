from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from _pytest import fixtures
from _pytest._code.code import Code
from _pytest._code.code import ExceptionInfo
from _pytest.python import CallSpec2
from _pytest.python import Class
from _pytest.python import Function
from _pytest.python import FunctionDefinition
from _pytest.python import Metafunc
from _pytest.python import Module
from _pytest.python import PyCollector

from .exceptions import UnableEvalParams
from .helper import Box
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

        if "given" in blocks:
            given_func = blocks["given"]
            given_argnames = Code.from_function(given_func).getargs()
            given_args = {}
            for argname in given_argnames:
                if argname == "me":
                    given_args["me"] = Box()
                else:
                    arg = self._request.getfixturevalue(argname)
                    self.funcargs[argname] = arg
                    given_args[argname] = arg

            given_func(**given_args)
            if given_args["me"]:
                self.funcargs.update(given_args["me"]._data)

        for block_name in ["when", "then", "expect", "cleanup"]:
            block_func = blocks.get(block_name)
            if block_func is None:
                continue
            block_argnames = Code.from_function(block_func).getargs()
            for argname in block_argnames:
                if argname not in self.funcargs:
                    if argname == "excinfo":
                        continue
                    self.funcargs[argname] = self._request.getfixturevalue(argname)

    def teardown(self) -> None:
        super().teardown()
        testfunc = self.obj
        if testfunc.__name__ == "__spock_failed__":
            return
        blocks = get_functions_in_function(testfunc)

        if "cleanup" not in blocks:
            return

        cleanup_func = blocks["cleanup"]
        cleanup_argnames = Code.from_function(cleanup_func).getargs()
        funcargs = self.funcargs
        cleanup_args = {arg: funcargs[arg] for arg in cleanup_argnames}
        cleanup_func(**cleanup_args)

    def runtest(self) -> None:
        testfunc = self.obj
        blocks = get_functions_in_function(testfunc)

        if "expect" not in blocks and "then" not in blocks:
            raise RuntimeError("No `expect` or `then` block found")

        if "expect" in blocks:
            expect_func = blocks["expect"]
            expect_argnames = Code.from_function(expect_func).getargs()
            funcargs = self.funcargs
            testargs = {arg: funcargs[arg] for arg in expect_argnames}
            expect_func(**testargs)

        if "when" in blocks:
            when_func = blocks["when"]
            funcargs = dict(self.funcargs)
            when_argnames = Code.from_function(when_func).getargs()
            when_args = {arg: funcargs[arg] for arg in when_argnames}
            excinfo: Optional[ExceptionInfo] = None
            try:
                when_func(**when_args)
            except:  # noqa: E722
                excinfo = ExceptionInfo.from_current()

            then_func = blocks.get("then")
            if then_func is None:
                return
            funcargs["excinfo"] = excinfo
            then_argnames = Code.from_function(then_func).getargs()
            then_args = {arg: funcargs[arg] for arg in then_argnames}
            then_func(**then_args)


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

            def __spock_failed__(idx: int = idx) -> None:

                raise ValueError(f"Unable to eval index {idx} params")  # pragma: no cover

            id = f"{name}[unable to eval {idx} params]"
            yield SpockFunction.from_parent(
                collector,
                name=id,
                callobj=__spock_failed__,
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
