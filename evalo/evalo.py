import structlog
import ast
from types import FunctionType
from uuid import uuid4

from kanren import eq, vars, goalify, isvar, var, run, unifiable, lany, \
    lall, membero, conde
from kanren.arith import add, sub, mul, div, mod
from kanren.core import EarlyGoalError, success, fail
from kanren.goals import heado, tailo, appendo, seteq
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


def eval_programo(program, env, value, depth=0, maxdepth=3):
    logger.info('Evaluating program {} to {} with env {}'.format(program, value, env))

    uuid = str(uuid4())[:4]
    stmt = var('stmt' + uuid)
    stmts = var('stmts' + uuid)

    if isinstance(program, ast.AST):
        logger.info('Found AST for program -> {}'.format(ast.dump(program)))
    if isinstance(value, ast.AST):
        logger.info('Found AST for program value -> {}'.format(ast.dump(value)))

    if depth == maxdepth:
        logger.debug('Depth {} reached, which is the maximum depth'.format(depth))
        return fail

    return (conde,
        ((eq, program, ast.Module(body=stmts)),
         (seteq, stmts, (stmt,)),  # Only support single stmt
         (eval_stmto, stmt, env, value)),
        #((eq, program, ast.Module(body=stmts)),
        # (eval_stmt_listo, stmts, env, value)),
    )


def eval_stmt_listo(stmts, env, value):
    logger.info('Evaluating stmt list {} to {} with env {}'.format(stmts, value, env))

    if isinstance(stmts, ast.AST):
        logger.info('Found AST for stmt list -> {}'.format(ast.dump(stmts)))
    if isinstance(value, ast.AST):
        logger.info('Found AST for stmt list value -> {}'.format(ast.dump(value)))

    uuid = str(uuid4())[:4]
    stmt = var('stmt' + uuid)
    tail = var('tailstmts' + uuid)
    return (conde,
        ((heado, stmt, stmts),
         (eval_stmto, stmt, env, value)),
        ((tailo, tail, stmts),
         (eval_stmt_listo, tail, env, value))
    )


def eval_stmto(stmt, env, value, depth=0, maxdepth=3):
    logger.info('Evaluating stmt {} to {} with env {}'.format(stmt, value, env))

    uuid = str(uuid4())[:4]
    exprbody = var('exprbody' + uuid)

    if isinstance(stmt, ast.AST):
        logger.info('Found AST for stmt -> {}'.format(ast.dump(stmt)))
    if isinstance(value, ast.AST):
        logger.info('Found AST for stmt value -> {}'.format(ast.dump(value)))

    if depth == maxdepth:
        logger.info('Depth {} reached, which is the maximum depth'.format(depth))
        return fail

    return (conde,
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
    body = var('body' + uuid)
    body_v = var('body_v' + uuid)
    func = var('func' + uuid)
    func_v = var('func_v' + uuid)
    if isinstance(expr, ast.AST):
        logger.info('Found AST for expr -> {}'.format(ast.dump(expr)))
    if isinstance(value, ast.AST):
        logger.info('Found AST for expr value -> {}'.format(ast.dump(value)))

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
