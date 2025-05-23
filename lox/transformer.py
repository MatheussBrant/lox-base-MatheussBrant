"""
Implementa o transformador da árvore sintática que converte entre as representações

    lark.Tree -> lox.ast.Node.

A resolução de vários exercícios requer a modificação ou implementação de vários
métodos desta classe.
"""

from typing import Callable
from lark import Transformer, v_args

from . import runtime as op
from .ast import *


def op_handler(op: Callable):
    """
    Fábrica de métodos que lidam com operações binárias na árvore sintática.

    Recebe a função que implementa a operação em tempo de execução.
    """

    def method(self, left, right):
        return BinOp(left, right, op)

    return method


@v_args(inline=True)
class LoxTransformer(Transformer):
    # Programa
    def program(self, *stmts):
        return Program(list(stmts))

    # Operações matemáticas básicas
    mul = op_handler(op.mul)
    div = op_handler(op.truediv)
    sub = op_handler(op.sub)
    add = op_handler(op.add)

    # Comparações
    gt = op_handler(op.gt)
    lt = op_handler(op.lt)
    ge = op_handler(op.ge)
    le = op_handler(op.le)
    eq = op_handler(op.eq)
    ne = op_handler(op.ne)

    # Operadores lógicos
    def or_(self, left: Expr, right: Expr):
        return Or(left, right)

    def and_(self, left: Expr, right: Expr):
        return And(left, right)

    def not_(self, right: Expr):
        if isinstance(right, Call):
            return Call(UnaryOp(op.not_, right.callee), right.params)
        return UnaryOp(op.not_, right)

    def neg(self, right: Expr):
        if isinstance(right, Call):
            return Call(UnaryOp(op.neg, right.callee), right.params)
        return UnaryOp(op.neg, right)

    # Atribuição
    def assign(self, name: Var, expr: Expr):
        return Assign(name.name, expr)

    # Atribuição de atributo
    def setattr(self, obj: Expr, attr: Var, value: Expr):
        return Setattr(obj, attr.name, value)

    # Acesso a atributo
    def getattr(self, obj: Expr, attr: Var):
        return Getattr(obj, attr.name)

    def call(self, callee: Expr, params: list):
        return Call(callee, params)

    def params(self, *args):
        return list(args)

    # Comandos
    def print_cmd(self, expr):
        return Print(expr)

    def VAR(self, token):
        return Var(str(token))

    def NUMBER(self, token):
        return Literal(float(token))

    def STRING(self, token):
        return Literal(str(token)[1:-1])

    def NIL(self, _):
        return Literal(None)

    def BOOL(self, token):
        return Literal(token == "true")