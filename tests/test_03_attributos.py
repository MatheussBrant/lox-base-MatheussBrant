from types import SimpleNamespace

import pytest
from lark import Tree

from lox import *
from lox import testing
from lox.ast import *


@pytest.fixture
def expr():
    return True


@pytest.fixture
def src():
    return "obj.attr"


@pytest.fixture
def src_():
    return "(x + y).attr"


def test_suporta_acesso_simples_a_atributo_na_cst(cst: Tree):
    assert "obj" in cst.pretty()
    assert "attr" in cst.pretty()


def test_suporta_acesso_a_atributo_na_cst(cst_: Tree):
    assert "x" in cst_.pretty()
    assert "y" in cst_.pretty()
    assert "attr" in cst_.pretty()


def test_suporta_acesso_atributo_na_ast(ast):
    assert isinstance(ast, Getattr)


def test_ast_salva_nome_do_atributo_como_string(ast_: Getattr):
    types = set(map(type, ast_.__dict__.values()))
    if str not in types:
        msg = f"O nome do atributo deve ser uma string, mas achei atributos dos tipos: {types}"
        raise ValueError(msg)


def test_implementa_a_função_eval(ast: Expr, ast_: Expr):
    obj = SimpleNamespace(attr=42)
    print(f"Testando com {obj=}")
    assert ast.eval(Ctx.from_dict({"obj": obj})) == 42  # type: ignore

    obj = SimpleNamespace(attr="ok")
    print(f"Testando com {obj=}")
    assert ast.eval(Ctx.from_dict({"obj": obj})) == "ok"  # type: ignore

    class Num(float):
        def __add__(self, other):
            return Num(super().__add__(other))

        @property
        def attr(self):
            return int(self)

    x = Num(3)
    y = Num(0.1415)
    print(f"Testando com {x=}, {y=}")
    assert ast_.eval(Ctx.from_dict({"x": x, "y": y})) == (x + y).attr  # type: ignore


class TestExamples(testing.ExampleTester):
    module = "field"
    examples = {
        "get_on_bool",
        "get_on_nil",
        "get_on_num",
        "get_on_string",
        "set_on_bool",
        "set_on_nil",
        "set_on_num",
        "set_on_string",
    }
