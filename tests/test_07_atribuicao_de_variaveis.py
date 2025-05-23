import pytest
from lark import Tree

from lox import *
from lox.ast import *


@pytest.fixture
def expr():
    return True


@pytest.fixture
def src():
    return "x = 42"


@pytest.fixture
def src_():
    return "y = x and y"


@pytest.fixture
def src__():
    return "x = y = z = 42"


def test_suporta_atribuição_na_gramática(cst: Tree, cst_):
    print(pretty := cst.pretty())
    assert "x" in pretty
    assert "42" in pretty

    print(pretty := cst_.pretty())
    assert "y" in pretty
    assert "x" in pretty


def test_suporta_atribuições_aninhadas(cst__):
    print(pretty := cst__.pretty())
    assert "x" in pretty
    assert "y" in pretty
    assert "z" in pretty
    assert "42" in pretty


def test_suporta_construção_de_ast(astf, ast_f, ast__f):
    cls = Assign
    assert isinstance(
        astf(), cls
    ), "Use a classe Assign para representar atribuições simples"
    assert isinstance(
        ast_f(), cls
    ), "Assign deve aceitar expressões arbitrárias do lado direito da atribuição"
    assert isinstance(ast__f(), cls), "Assign deve suportar atribuições aninhadas"


def test_atribuição_modifica_o_contexto(ast):
    ctx = Ctx.from_dict({"x": 0})
    ast.eval(ctx)
    assert ctx["x"] == 42, "Atribuição não modificou o contexto corretamente"


def test_atribuição_avalia_como_o_lado_direito(ast):
    ctx = Ctx.from_dict({"x": 0})
    assert ast.eval(ctx) == 42


def test_implementa_a_função_eval(exs):
    def ctx():
        return Ctx.from_dict({"x": True, "y": False, "z": True})

    results = [42, False, 42]
    for expect, ex in zip(results, exs):
        print(f"Testando {ex.src=}")
        result = ex.ast.eval(ctx())

        assert (
            result == expect
        ), f"[Assign.eval]: esperava {expect} mas encontrei {result}"
