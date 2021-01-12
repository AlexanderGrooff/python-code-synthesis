import ast
from operator import add, sub, mul, mod
from types import FunctionType
from uuid import uuid4

from unification.core import isground

from kanren.constraints import (
    isinstanceo,
    ConstrainedState,
    neq,
)
from kanren.term import applyo
from loguru import logger
from kanren import eq, var, unifiable, membero, conde

from kanren.core import fail
from kanren.goals import heado, tailo
from unification import reify

from evalo.utils import rec_ast_parse

unifiable(ast.AST)


def binopo(x, y, v, op):
    def isnumber(n):
        return isinstance(n, int) or isinstance(n, float)

    def binopo_goal(S: ConstrainedState):
        nonlocal x, y, v, op

        x_rf, y_rf, v_rf, op_rf = reify((x, y, v, op), S)
        isground_all = [
            isground(reified_value, S) for reified_value in [x_rf, y_rf, v_rf, op_rf]
        ]
        if not all(isground_all):
            # We can only fix one LV at a time
            if len([uv for uv in isground_all if uv is False]) == 1:
                # TODO: Revop the other vars
                if not isground(v_rf, S):
                    g = eq(op_rf(x_rf, y_rf), v_rf)
                    yield from g(S)
        else:
            # TODO: Why isnt this covered by the `isinstanceo` goal?
            if isnumber(x_rf) and isnumber(y_rf) and isnumber(v_rf):
                if op_rf(x_rf, y_rf) == v_rf:
                    yield S

    return binopo_goal


def evalo(program, value):
    unifiable(ast.AST)
    return eval_programo(program, [], value)


def eval_programo(program, env, value):
    logger.info("Evaluating program {} to {} with env {}".format(program, value, env))

    # fmt: off
    return conde(
        (eval_stmto(program, env, value),),  # Change this
    )
    # fmt: on


def eval_stmto(stmt, env, value):
    logger.info("Evaluating stmt {} to {} with env {}".format(stmt, value, env))

    exprbody = var("exprbody")
    # fmt: off
    return conde(
        (eq(stmt, ast.Expr(value=exprbody)),  # Expressions
         eval_expro(exprbody, env, value)),
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
        (eq(expr, ast.Str(s=str_e)),
         isinstanceo(value, str),
         eq(str_e, value)),
        (eq(expr, ast.Num(n=value)),
         membero(value, [_ for _ in range(5)])),
        (eq(expr, ast.BinOp(left=e1, op=var('op_e_' + uuid), right=e2)),
         isinstanceo(v1, int),
         isinstanceo(v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         eval_opo(var('op_e_' + uuid), var('op_v_' + uuid), v1, v2, value),
         binopo(v1, v2, value, op=var('op_v_' + uuid))),
        (eq(expr, ast.Call(func=func, args=[], keywords=[])),
         isinstanceo(func_v, FunctionType),
         eval_expro(func, env, func_v, depth + 1, maxdepth),
         applyo(func_v, [], value)),
        (eq(expr, ast.Lambda(body=body, args=[])),
         isinstanceo(value, FunctionType),
         eval_expro(body, env, body_v, depth + 1, maxdepth),
         eq(lambda: body_v, value)),
    )
    # fmt: on


def eval_opo(op, value, v1, v2, v):
    # Extra args for future use
    # fmt: off
    return conde(
        (eq(op, ast.Add()),
         eq(value, add)),
        (eq(op, ast.Sub()),
         eq(value, sub)),
        (eq(op, ast.Mult()),
         eq(value, mul)),
        (eq(op, ast.Mod()),
         neq(v2, 0),  # Prevent division by zero
         eq(value, mod)),
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
