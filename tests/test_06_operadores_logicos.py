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
    return "x and f()"


@pytest.fixture
def src_():
    return "y or g()"


@pytest.fixture
def src__():
    return "z > a and z < b"


def test_suporta_operador_and(cst: Tree):
    print(pretty := cst.pretty())
    assert "x" in pretty
    assert "f" in pretty


def test_suporta_o_operador_or(cst_: Tree):
    print(pretty := cst_.pretty())
    assert "y" in pretty
    assert "g" in pretty


def test_suporta_comparações_nos_argumentos(cst__: Tree):
    print(pretty := cst__.pretty())
    assert "z" in pretty
    assert "a" in pretty
    assert "b" in pretty


def test_suporta_construção_de_ast(ast, ast_, ast__):
    assert isinstance(
        ast, And
    ), "Use a classe And para representar operações lógicas AND"
    assert isinstance(ast_, Or), "Use a classe Or para representar operações lógicas OR"
    assert isinstance(
        ast__, And
    ), "Você deve suportar comparações nos argumentos dos operadores."


def test_avaliação_de_curto_circuito(ast, ast_):
    def raises():
        raise RecursionError("Curto-circuito: não deveria avaliar essa função")

    ctx = Ctx.from_dict({"x": False, "f": raises})
    assert ast.eval(ctx) is False

    ctx = Ctx.from_dict({"y": True, "g": raises})
    assert ast_.eval(ctx) is True


def test_implementa_a_função_eval(exs):
    def ctx_true():
        return Ctx.from_dict(
            {
                "x": True,
                "f": lambda: True,
                "y": False,
                "g": lambda: True,
                "z": 1,
                "a": 0,
                "b": 2,
            }
        )

    def ctx_false():
        return Ctx.from_dict(
            {
                "x": True,
                "f": lambda: False,
                "y": False,
                "g": lambda: False,
                "z": 3,
                "a": 0,
                "b": 2,
            }
        )

    for ex in exs:
        print(f"Testando {ex.src=}")
        result = ex.ast.eval(ctx_true())
        assert result, f"[Call.eval]: esperava True mas encontrei {result}"

    for ex in exs:
        print(f"Testando {ex.src=}")
        result = ex.ast.eval(ctx_false())
        assert not result, f"[Call.eval]: esperava False mas encontrei {result}"


class TestExamples(testing.ExampleTester):
    module = "logical_operator"
    examples = {"and_truth", "or_truth"}
