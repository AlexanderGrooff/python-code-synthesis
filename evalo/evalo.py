import ast
from types import FunctionType
from uuid import uuid4

from loguru import logger
from kanren import eq, goalify, isvar, var, unifiable, membero, conde
from kanren.arith import add, sub, mul, mod
from kanren.core import EarlyGoalError, fail
from kanren.goals import heado, tailo

from evalo.utils import rec_ast_parse

typeo = goalify(type)

unifiable(ast.AST)


def callo(func, val):
    if not isvar(func):
        return eq, func(), val
    raise EarlyGoalError()


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
    logger.debug("Evaluating expr {} to {} with env {}".format(expr, value, env))
    uuid = str(uuid4())[:4]

    if isinstance(expr, ast.AST):
        logger.info("Found AST for expr -> {}".format(rec_ast_parse(expr)))
    if isinstance(value, ast.AST):
        logger.info("Found AST for value -> {}".format(rec_ast_parse(value)))

    if depth == maxdepth:
        logger.debug("Depth {} reached, which is the maximum depth".format(depth))
        return fail
    # fmt: off
    return (conde,
        ((eq, expr, ast.Name(id=var("name" + uuid), ctx=ast.Load())),
         (lookupo, var("name" + uuid), env, value)),
        ((eq, expr, ast.Str(s=var("str_e" + uuid))),
         (typeo, value, str),
         (eq, var("str_e" + uuid), value)),
        ((eq, expr, ast.Num(n=value)),
         (membero, value, range(5))),
        ((eq, expr, ast.BinOp(left=var("add_e1_" + uuid), op=ast.Add(), right=var("add_e2_" + uuid))),
         (typeo, var("add_v1_" + uuid), int),
         (typeo, var("add_v2_" + uuid), int),
         eval_expro(var("add_e1_" + uuid), env, var("add_v1_" + uuid), depth + 1, maxdepth),
         eval_expro(var("add_e2_" + uuid), env, var("add_v2_" + uuid), depth + 1, maxdepth),
         (add, var("add_v1_" + uuid), var("add_v2_" + uuid), value)),
        ((eq, expr, ast.BinOp(left=var("sub_e1_" + uuid), op=ast.Sub(), right=var("sub_e2_" + uuid))),
         (typeo, var("sub_v1_" + uuid), int),
         (typeo, var("sub_v2_" + uuid), int),
         eval_expro(var("sub_e1_" + uuid), env, var("sub_v1_" + uuid), depth + 1, maxdepth),
         eval_expro(var("sub_e2_" + uuid), env, var("sub_v2_" + uuid), depth + 1, maxdepth),
         (sub, var("sub_v1_" + uuid), var("sub_v2_" + uuid), value)),
        ((eq, expr, ast.BinOp(left=var("mult_e1_" + uuid), op=ast.Mult(), right=var("mult_e2_" + uuid))),
         (typeo, var("mult_v1_" + uuid), int),
         (typeo, var("mult_v2_" + uuid), int),
         eval_expro(var("mult_e1_" + uuid), env, var("mult_v1_" + uuid), depth + 1, maxdepth),
         eval_expro(var("mult_e2_" + uuid), env, var("mult_v2_" + uuid), depth + 1, maxdepth),
         (mul, var("mult_v1_" + uuid), var("mult_v2_" + uuid), value)),
        ((eq, expr, ast.BinOp(left=var("mod_e1_" + uuid), op=ast.Mod(), right=var("mod_e2_" + uuid))),
         eval_expro(var("mod_e1_" + uuid), env, var("mod_v1_" + uuid), depth + 1, maxdepth),
         eval_expro(var("mod_e2_" + uuid), env, var("mod_v2_" + uuid), depth + 1, maxdepth),
         (mod, var("mod_v1_" + uuid), var("mod_v2_" + uuid), value)),
        ((eq, expr, ast.Call(func=var("func" + uuid), args=[], keywords=[])),
         (typeo, var("func_v" + uuid), FunctionType),
         eval_expro(var("func" + uuid), env, var("func_v" + uuid), depth + 1, maxdepth),
         (callo, var("func_v" + uuid), value)),
        ((eq, expr, ast.Lambda(body=var("body" + uuid), args=[])),
         (typeo, value, FunctionType),
         eval_expro(var("body" + uuid), env, var("body_v" + uuid), depth + 1, maxdepth),
         (eq, lambda: var("body_v" + uuid), value)),
    )
    # fmt: on


def lookupo(name, env, t):
    head = var()
    rest = var()
    key = var()
    val = var()
    # fmt: off
    return (conde,
        ((heado, head, env),
         (heado, name, head),
         (tailo, rest, head),
         (heado, t, rest)),
        ((tailo, rest, env),
         (lookupo, name, rest, t))
    )
    # fmt: on
