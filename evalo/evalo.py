import structlog
import ast
from types import FunctionType
from uuid import uuid4

from kanren import eq, vars, goalify, isvar, var, run, unifiable, lany, \
    lall, membero, conde
from kanren.arith import add, sub, mul, div, mod
from kanren.core import EarlyGoalError, success, fail
from kanren.goals import heado, tailo, appendo
from unification.more import unify_object

import evalo.logging
from evalo.utils import debugo

logger = structlog.get_logger()
typeo = goalify(type)

unifiable(ast.AST)


def callo(func, val):
    if not isvar(func):
        return (eq, func(), val)
    raise EarlyGoalError()


def evalo(program, value):
    unifiable(ast.AST)
    return eval_programo(program, [], value)


def eval_programo(program, env, value):
    logger.info('Evaluating program {} to {} with env {}'.format(program, value, env))

    return conde(
        ((eval_stmto, program, env, value),),  # Change this
    )


def eval_stmto(stmt, env, value):
    logger.info('Evaluating stmt {} to {} with env {}'.format(stmt, value, env))

    exprbody = var('exprbody')
    return conde(
        ((eq, stmt, ast.Expr(value=exprbody)),  # Expressions
         (eval_expro, exprbody, env, value)),
    )


def eval_expro(expr, env, value, depth=0, maxdepth=3):
    logger.debug('Evaluating expr {} to {} with env {}'.format(expr, value, env))
    uuid = str(uuid4())[:4]
    v1 = var('v1' + uuid)
    v2 = var('v2' + uuid)
    e1 = var('e1' + uuid)
    e2 = var('e2' + uuid)
    op = var('op' + uuid)
    op_v = var('op_v' + uuid)
    name = var('name' + uuid)
    str_e = var('str_e' + uuid)
    func = var('func' + uuid)
    func_v = var('func_v' + uuid)
    if isinstance(expr, ast.AST):
        logger.info('Found AST for expr -> {}'.format(ast.dump(expr)))
    if isinstance(value, ast.AST):
        logger.info('Found AST for value -> {}'.format(ast.dump(value)))

    if depth == maxdepth:
        logger.debug('Depth {} reached, which is the maximum depth'.format(depth))
        return fail
    return (conde,
        ((eq, expr, ast.Name(id=name, ctx=ast.Load())),
         (lookupo, name, env, value)),
        ((eq, expr, ast.Str(s=str_e)),
         (typeo, value, str),
         (eq, str_e, value)),
        ((eq, expr, ast.Num(n=value)),
         (membero, value, range(5))),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Add(), right=e2)),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (add, v1, v2, value)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Sub(), right=e2)),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (sub, v1, v2, value)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Mult(), right=e2)),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (mul, v1, v2, value)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Mod(), right=e2)),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (mod, v1, v2, value)),
        ((eq, expr, ast.Call(func=func, args=[], keywords=[])),
         eval_funco(func, env, func_v, depth + 1, maxdepth),
         (callo, func_v, value))
    )


def eval_funco(func, env, value, depth, maxdepth=3):
    logger.debug('Evaluating func {} to {} with env {}'.format(func, value, env))
    uuid = str(uuid4())[:4]
    body = var('body' + uuid)
    body_v = var('body_v' + uuid)

    if depth == maxdepth:
        logger.debug('Depth {} reached, which is the maximum depth'.format(depth))
        return fail

    return (conde,
        ((eq, func, ast.Lambda(body=body, args=[])),
         (typeo, value, FunctionType),
         eval_expro(body, env, body_v, depth + 1, maxdepth),
         (eq, lambda: body_v, value)),
    )


def lookupo(name, env, t):
    head = var()
    rest = var()
    key = var()
    val = var()
    return (conde,
        ((heado, head, env),
         (heado, name, head),
         (tailo, rest, head),
         (heado, t, rest)),
        ((tailo, rest, env),
         (lookupo, name, rest, t))
    )
