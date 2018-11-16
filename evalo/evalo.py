import structlog
import ast
from types import FunctionType
from uuid import uuid4

from kanren import eq, vars, goalify, isvar, var, run, unifiable, lany, \
    lall, membero, conde
from kanren.arith import add, sub, mul, div, mod
from kanren.core import EarlyGoalError, success, fail, everyg
from kanren.goals import heado, tailo, appendo, conso
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
    list_e = var('list_e' + uuid)
    op = var('op' + uuid)
    op_v = var('op_v' + uuid)
    name = var('name' + uuid)
    str_e = var('str_e' + uuid)
    body = var('body' + uuid)
    body_v = var('body_v' + uuid)
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
        ((eq, expr, ast.List(elts=list_e)),
         (typeo, list_e, list),
         eval_seqo(list_e, env, value, depth + 1, maxdepth)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Add(), right=e2)),
         (typeo, v1, int),
         (typeo, v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (add, v1, v2, value)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Sub(), right=e2)),
         (typeo, v1, int),
         (typeo, v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (sub, v1, v2, value)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Mult(), right=e2)),
         (typeo, v1, int),
         (typeo, v2, int),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (mul, v1, v2, value)),
        ((eq, expr, ast.BinOp(left=e1, op=ast.Mod(), right=e2)),
         eval_expro(e1, env, v1, depth + 1, maxdepth),
         eval_expro(e2, env, v2, depth + 1, maxdepth),
         (mod, v1, v2, value)),
        ((eq, expr, ast.Call(func=func, args=[], keywords=[])),
         (typeo, func_v, FunctionType),
         eval_expro(func, env, func_v, depth + 1, maxdepth),
         (callo, func_v, value)),
        ((eq, expr, ast.Lambda(body=body, args=[])),
         (typeo, value, FunctionType),
         eval_expro(body, env, body_v, depth + 1, maxdepth),
         (eq, lambda: body_v, value)),
    )


def eval_seqo(l, env, val, depth, maxdepth):
    uuid = str(uuid4())[:4]
    head_e = var('head_e' + uuid)
    head_v = var('head_v' + uuid)
    tail_e = var('tail_e' + uuid)
    tail_v = var('tail_v' + uuid)
    if depth == maxdepth:
        logger.debug('Depth {} reached, which is the maximum depth'.format(depth))
        return fail

    return (conde,
        ((eq, l, []),
         (eq, val, [])),
        ((conso, head_e, tail_e, l),
         eval_expro(head_e, env, head_v, depth + 1, maxdepth),
         eval_seqo(tail_e, env, tail_v, depth + 1, maxdepth),
         (conso, head_v, tail_v, val),
         (debugo, val)),
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
