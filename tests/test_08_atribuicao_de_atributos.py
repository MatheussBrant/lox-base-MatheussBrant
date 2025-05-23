from types import SimpleNamespace

import pytest
from lark import Tree

from lox import *
from lox.ast import *


@pytest.fixture
def expr():
    return True


@pytest.fixture
def src():
    return "x.attr = 42"


@pytest.fixture
def src_():
    return "y.attr = x.attr"


@pytest.fixture
def src__():
    return "z.attr = y = x.attr = 42"


def test_suporta_atribuição_na_gramática(cst: Tree, cst_):
    print(pretty := cst.pretty())
    assert "x" in pretty
    assert "attr" in pretty
    assert "42" in pretty

    print(pretty := cst_.pretty())
    assert "x" in pretty
    assert "y" in pretty
    assert "attr" in pretty


def test_suporta_atribuições_aninhadas(cst__):
    print(pretty := cst__.pretty())
    assert "x" in pretty
    assert "y" in pretty
    assert "z" in pretty
    assert "attr" in pretty
    assert "42" in pretty


def test_suporta_construção_de_ast(astf, ast_f, ast__f):
    cls = Setattr
    assert isinstance(
        astf(), cls
    ), "Use a classe Setattr para representar atribuições de atributos"
    assert isinstance(
        ast_f(), cls
    ), "Setattr deve aceitar expressões arbitrárias do lado direito da atribuição"
    assert isinstance(ast__f(), cls), "Setattr deve suportar atribuições aninhadas"


def test_atribuição_modifica_o_objeto_e_nao_o_contexto(ast):
    ctx = Ctx.from_dict({"x": (x := SimpleNamespace(attr=0))})
    ast.eval(ctx)
    assert "attr" not in ctx, "Atribuição salvou o objeto no contexto"
    assert x.attr == 42, "Atribuição não modificou o objeto"


def test_atribuição_avalia_como_o_lado_direito(ast):
    ctx = Ctx.from_dict({"x": SimpleNamespace(attr=0)})
    assert ast.eval(ctx) == 42


def test_implementa_a_função_eval(exs):
    obj = SimpleNamespace

    def ctx():
        return Ctx.from_dict(
            {
                "x": (x := obj(attr=0)),
                "y": obj(attr=False),
                "z": obj(attr=x),
            }
        )

    results = [
        42,
        0,
        42,
    ]
    for expect, ex in zip(results, exs):
        print(f"Testando {ex.src=}")
        result = ex.ast.eval(ctx())

        assert (
            result == expect
        ), f"[Setattr.eval]: esperava {expect} mas encontrei {result}"
