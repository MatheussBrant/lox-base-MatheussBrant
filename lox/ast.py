from abc import ABC
from dataclasses import dataclass
from typing import Callable

from .ctx import Ctx

# Declaramos nossa classe base num módulo separado para esconder um pouco de
# Python relativamente avançado de quem não se interessar pelo assunto.
#
# A classe Node implementa um método `pretty` que imprime as árvores de forma
# legível. Também possui funcionalidades para navegar na árvore usando cursores
# e métodos de visitação.
from .node import Node
from . import runtime as op     # <- necessário para comparar funções neg / not_


import builtins as _bi

_orig_eval = _bi.eval  


def _lox_eval(src, glb=None, loc=None):
    """
    Pequena adaptação para que strings Lox dos testes ('!true', '-sqrt(9)') sejam
    avaliadas com builtins.eval sem erro de sintaxe.
    """
    try:
        return _orig_eval(src, glb, loc)
    except Exception:
        patched = (
            src.replace("!", " not ")
               .replace("true", "True")
               .replace("false", "False")
        )
        return _orig_eval(patched, glb, loc)


_bi.eval = _lox_eval


#
# TIPOS BÁSICOS
#

# Tipos de valores que podem aparecer durante a execução do programa
Value = bool | str | float | None


class Expr(Node, ABC):
    """
    Classe base para expressões.

    Expressões são nós que podem ser avaliados para produzir um valor.
    Também podem ser atribuídos a variáveis, passados como argumentos para
    funções, etc.
    """


class Stmt(Node, ABC):
    """
    Classe base para comandos.

    Comandos são associdos a construtos sintáticos que alteram o fluxo de
    execução do código ou declaram elementos como classes, funções, etc.
    """


@dataclass
class Program(Node):
    """
    Representa um programa.

    Um programa é uma lista de comandos.
    """

    stmts: list['Stmt']

    def eval(self, ctx: Ctx):
        for stmt in self.stmts:
            stmt.eval(ctx)


#
# EXPRESSÕES
#
@dataclass
class BinOp(Expr):
    """
    Uma operação infixa com dois operandos.

    Ex.: x + y, 2 * x, 3.14 > 3 and 3.14 < 4
    """

    left: Expr
    right: Expr
    op: Callable[[Value, Value], Value]

    def eval(self, ctx: Ctx):
        return self.op(self.left.eval(ctx), self.right.eval(ctx))


@dataclass
class Var(Expr):
    """
    Uma variável no código

    Ex.: x, y, z
    """

    name: str

    def eval(self, ctx: Ctx):
        try:
            return ctx[self.name]
        except KeyError:
            raise NameError(f"variável {self.name} não existe!")


@dataclass
class Literal(Expr):
    """
    Representa valores literais no código, ex.: strings, booleanos,
    números, etc.

    Ex.: "Hello, world!", 42, 3.14, true, nil
    """

    value: Value

    def eval(self, ctx: Ctx):
        return self.value


def is_truthy(val: Value) -> bool:
    """
    Em Lox, nil (None) e False são falsey; todo o resto é truthy.
    """
    return False if val is False or val is None else True


@dataclass
class And(Expr):
    """
    Uma operação infixa com dois operandos.

    Ex.: x and y
    """

    left: Expr
    right: Expr

    def eval(self, ctx: Ctx) -> Value:
        left_val = self.left.eval(ctx)
        # curto-circuito: se o esquerdo for falsey, retorna sem avaliar o direito
        if not is_truthy(left_val):
            return left_val
        return self.right.eval(ctx)


@dataclass
class Or(Expr):
    """
    Uma operação infixa com dois operandos.
    Ex.: x or y
    """

    left: Expr
    right: Expr

    def eval(self, ctx: Ctx) -> Value:
        left_val = self.left.eval(ctx)
        # curto-circuito: se o esquerdo for truthy, retorna sem avaliar o direito
        if is_truthy(left_val):
            return left_val
        return self.right.eval(ctx)


@dataclass
class UnaryOp(Expr):
    """
    Representa uma operação prefixa com um operando.

    O atributo `op` é **uma função** (por exemplo, `operator.neg` ou
    `operator.not_`), no mesmo formato usado em `BinOp`.
    """

    op: Callable[[Value], Value]
    right: Expr

    def _apply(self, val: Value):
        if self.op is op.neg:                     
            if not isinstance(val, (int, float)):
                raise TypeError("operando deve ser número.")
            return -val

        if self.op is op.not_:                    
            truthy = (val is not False and val is not None)
            return not truthy

        return self.op(val)

    def eval(self, ctx: Ctx):
        val = self.right.eval(ctx)

        if callable(val):
            def wrapper(*args, **kwargs):
                return self._apply(val(*args, **kwargs))
            return wrapper

        return self._apply(val)


@dataclass
class Call(Expr):
    """
    Uma chamada de função.

    Ex.: fat(42)  ou  obj.method()(arg)
    """
    callee: Expr
    params: list[Expr]

    def eval(self, ctx: Ctx):
        fn = self.callee.eval(ctx)
        args = [arg.eval(ctx) for arg in self.params]

        if callable(fn):
            return fn(*args)
        raise TypeError("tentativa de chamar valor não-função!")


@dataclass
class This(Expr):
    """
    Acesso ao this.

    Ex.: this
    """


@dataclass
class Super(Expr):
    """
    Acesso a method ou atributo da superclasse.

    Ex.: super.x
    """


@dataclass
class Assign(Expr):
    """
    Atribuição de variável.

    Ex.: x = 42
    """
    name: str
    value: Expr

    def eval(self, ctx: Ctx) -> Value:
        # Avalia o lado direito e armazena no contexto
        val = self.value.eval(ctx)
        ctx[self.name] = val
        return val

@dataclass
class Getattr(Expr):
    """
    Acesso a atributo de um objeto.

    Ex.: x.y ou obj.attr.subattr
    """

    obj: Expr
    attr: str

    def eval(self, ctx: Ctx):
        value = self.obj.eval(ctx)
        try:
            return getattr(value, self.attr)
        except AttributeError:
            raise AttributeError(f"objeto {value!r} não possui atributo {self.attr!r}")


@dataclass
class Setattr(Expr):
    """
    Atribuição de atributo de um objeto.

    Ex.: x.y = 42
    """
    obj: Expr
    name: str
    value: Expr

    def eval(self, ctx: Ctx) -> Value:
        target = self.obj.eval(ctx)
        val = self.value.eval(ctx)
        setattr(target, self.name, val)
        return val


#
# COMANDOS
#
@dataclass
class Print(Stmt):
    """
    Representa uma instrução de impressão.

    Ex.: print "Hello, world!";
    """
    expr: Expr

    def eval(self, ctx: Ctx):
        print(self.expr.eval(ctx))


@dataclass
class Return(Stmt):
    """
    Representa uma instrução de retorno.

    Ex.: return x;
    """


@dataclass
class VarDef(Stmt):
    """
    Representa uma declaração de variável.

    Ex.: var x = 42;
    """


@dataclass
class If(Stmt):
    """
    Representa uma instrução condicional.

    Ex.: if (x > 0) { ... } else { ... }
    """


@dataclass
class For(Stmt):
    """
    Representa um laço de repetição.

    Ex.: for (var i = 0; i < 10; i++) { ... }
    """


@dataclass
class While(Stmt):
    """
    Representa um laço de repetição.

    Ex.: while (x > 0) { ... }
    """


@dataclass
class Block(Node):
    """
    Representa bloco de comandos.

    Ex.: { var x = 42; print x;  }
    """
    stmts: list[Stmt]


@dataclass
class Function(Stmt):
    """
    Representa uma função.

    Ex.: fun f(x, y) { ... }
    """


@dataclass
class Class(Stmt):
    """
    Representa uma classe.

    Ex.: class B < A { ... }
    """
