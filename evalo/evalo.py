import ast
from collections import Sequence
from operator import add, sub, mul, mod
from types import FunctionType
from uuid import uuid4

from kanren.util import pprint
from unification.core import isground

from kanren.constraints import (
    isinstanceo,
    ConstrainedState,
    neq,
)
from kanren.term import applyo
from loguru import logger
from kanren import eq, var, unifiable, membero, conde

from kanren.core import fail, lall
from kanren.goals import heado, tailo
from unification import reify

from evalo.utils import rec_ast_parse

unifiable(ast.AST)


def binopo(x, y, v, op):
    def binopo_goal(S: ConstrainedState):
        nonlocal x, y, v, op

        x_rf, y_rf, v_rf = reify((x, y, v), S)
        if not (isground(x_rf, S) and isground(y_rf, S) and isground(v_rf, S)):
            if not isground(v_rf, S):
                g = eq(op(x_rf, y_rf), v_rf)
                yield from g(S)
        else:
            if op(x_rf, y_rf) == v_rf:
                yield S

    return binopo_goal


def evalo(program, value):
    unifiable(ast.AST)
    return eval_programo(program, [], value)


def eval_programo(program, env, value):
    logger.info("Evaluating program {} to {} with env {}".format(program, value, env))

    # fmt: off
    return conde(
        ((eval_stmto, program, env, value),),  # Change this
    )
    # fmt: on


def eval_stmto(stmt, env, value):
    logger.info("Evaluating stmt {} to {} with env {}".format(stmt, value, env))

    exprbody = var("exprbody")
    # fmt: off
    return conde(
        ((eq, stmt, ast.Expr(value=exprbody)),  # Expressions
         (eval_expro, exprbody, env, value)),
    )
    # fmt: on


def eval_expro(expr, env, value, depth=0, maxdepth=3):
    # logger.debug("Evaluating expr {} to {} with env {}".format(expr, value, env))
    uuid = str(uuid4())[:4]
    v1 = var("v1" + uuid)
    v2 = var("v2" + uuid)
    e1 = var("e1" + uuid)
    e2 = var("e2" + uuid)
    name = var("name" + uuid)
    str_e = var("str_e" + uuid)
    body = var("body" + uuid)
    body_v = var("body_v" + uuid)
    func = var("func" + uuid)
    func_v = var("func_v" + uuid)
    if isinstance(expr, ast.AST):
        logger.info("Found AST for expr -> {}".format(rec_ast_parse(expr)))
    if isinstance(value, ast.AST):
        logger.info("Found AST for value -> {}".format(rec_ast_parse(value)))

    if depth >= maxdepth:
        return fail
    # fmt: off
    return conde(
        (eq(expr, ast.Name(id=name, ctx=ast.Load())),
         lookupo(name, env, value)),
        # ((eq, expr, ast.Str(s=str_e)),
        #  (typeo, value, str),
        #  (eq, str_e, value)),
        (eq(expr, ast.Num(n=value)),
         membero(value, [_ for _ in range(5)])),
        (eq(expr, ast.BinOp(left=e1, op=ast.Add(), right=e2)),
         isinstanceo(v1, int),
         isinstanceo(v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         binopo(v1, v2, value, op=add)),
        (eq(expr, ast.BinOp(left=e1, op=ast.Sub(), right=e2)),
         isinstanceo(v1, int),
         isinstanceo(v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         binopo(v1, v2, value, op=sub)),
        (eq(expr, ast.BinOp(left=e1, op=ast.Mult(), right=e2)),
         isinstanceo(v1, int),
         isinstanceo(v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         binopo(v1, v2, value, op=mul)),
        (eq(expr, ast.BinOp(left=e1, op=ast.Mod(), right=e2)),
         isinstanceo(v1, int),
         isinstanceo(v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         neq(v2, 0),  # Don't divide by zero
         binopo(v1, v2, value, op=mod)),
        # (eq(expr, ast.Call(func=func, args=[], keywords=[])),
        #  isinstanceo(func_v, FunctionType),
        #  eval_expro(func, env, func_v, depth + 1, maxdepth),
        #  applyo(func_v, [], value)),
        # (eq(expr, ast.Lambda(body=body, args=[])),
        #  isinstanceo(value, FunctionType),
        #  eval_expro(body, env, body_v, depth + 1, maxdepth),
        #  eq(lambda: body_v, value)),
    )
    # fmt: on


def lookupo(name, env, t, depth=0, maxdepth=100):
    if depth >= maxdepth:
        return fail

    head = var()
    rest = var()
    # fmt: off
    return conde(
        (heado(head, env),
         heado(name, head),
         tailo(rest, head),
         heado(t, rest)),
        (tailo(rest, env),
         lookupo(name, rest, t, depth + 1, maxdepth))
    )
    # fmt: on
