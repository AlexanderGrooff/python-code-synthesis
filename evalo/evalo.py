import ast
from types import FunctionType
from typing import List, Union
from uuid import uuid4

from loguru import logger
from kanren import eq, isvar, var, unifiable, membero, conde
from kanren.arith import add, sub, mul, mod
from kanren.core import EarlyGoalError, fail
from kanren.goals import heado, tailo, conso, LCons
from unification import Var

from evalo.utils import ast_dump_if_possible

unifiable(ast.AST)


# typeo = goalify(type) doesn't cut it, because it tries to unnest the first parameter because it's a possible list
# It works for str, int etc but not for iterables such as list, tuple
def typeo(x, t):
    if isvar(x):
        raise EarlyGoalError()
    return eq, type(x), t


def tuple_to_listo(t, l):
    if isvar(t) and isvar(l):
        raise EarlyGoalError()
    if isvar(t):
        def list_to_tuple(old_list):
            new_list = [list_to_tuple(x) if isinstance(x, list) else x for x in old_list]
            return (*new_list,)
        return eq, t, list_to_tuple(l)
    if isvar(l):
        def tuple_to_list(old_tuple):
            return [tuple_to_list(x) if isinstance(x, tuple) else x for x in old_tuple]
        return eq, tuple_to_list(t), l


def callo(func, val, *args):
    if not isvar(func):
        return eq, func(*args), val
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
    logger.info(
        "Evaluating stmt {} to {} with env {}".format(
            ast_dump_if_possible(stmt),
            ast_dump_if_possible(value),
            ast_dump_if_possible(env),
        )
    )
    uuid = str(uuid4())[:4]

    new_env = var("new_env_" + uuid)
    # fmt: off
    goals = (conde,
        ((eq, stmt, ast.Assign(targets=var("assign_targets_" + uuid), value=var("assign_value_" + uuid))),
         (heado, var("assign_lhs_" + uuid), var("assign_targets_" + uuid)),  # TODO: Allow for multiple assigns: a, b, = ...
         (eval_expro, var("assign_value_" + uuid), env, var("assign_rhs_" + uuid)),
         (conso, [var("assign_lhs_" + uuid), var("assign_rhs_" + uuid)], env, new_env)),  # new_env = [lhs, rhs] + env
        ((eq, stmt, ast.Expr(value=var("exprbody" + uuid))),  # Expressions
         (eval_expro, var("exprbody" + uuid), env, value)),
    )
    return goals, new_env
    # fmt: on


def eval_expro(expr, env, value, depth=0, maxdepth=3):
    # logger.debug("Evaluating expr {} to {} with env {}".format(expr, value, env))
    uuid = str(uuid4())[:4]

    if isinstance(expr, ast.AST):
        logger.info("Found AST for expr -> {}".format(ast_dump_if_possible(expr)))
    if isinstance(value, ast.AST):
        logger.info("Found AST for value -> {}".format(ast_dump_if_possible(value)))

    if depth >= maxdepth:
        # logger.debug("Depth {} reached, which is the maximum depth".format(depth))
        return fail
    # fmt: off
    return (conde,
        ((eq, expr, ast.Name(id=var("name" + uuid), ctx=ast.Load())),
         # Handle ast.Store in ast.Assign statement
         (lookupo, var("load_name_" + uuid), env, value)),

        ((eq, expr, ast.Str(s=var("str_e_" + uuid))),
         (typeo, value, str),
         (eq, var("str_e_" + uuid), value)),
        # Numbers
        ((eq, expr, ast.Num(n=value)),
         (typeo, value, int),
         (membero, value, range(5))),
        ((eq, expr, ast.BinOp(left=var("add_e1_" + uuid), op=ast.Add(), right=var("add_e2_" + uuid))),
         (typeo, var("add_v1_" + uuid), int),
         (typeo, var("add_v2_" + uuid), int),
         (eval_expro, var("add_e1_" + uuid), env, var("add_v1_" + uuid), depth + 1, maxdepth),
         (eval_expro, var("add_e2_" + uuid), env, var("add_v2_" + uuid), depth + 1, maxdepth),
         (add, var("add_v1_" + uuid), var("add_v2_" + uuid), value)),
        ((eq, expr, ast.BinOp(left=var("sub_e1_" + uuid), op=ast.Sub(), right=var("sub_e2_" + uuid))),
         (typeo, var("sub_v1_" + uuid), int),
         (typeo, var("sub_v2_" + uuid), int),
         (eval_expro, var("sub_e1_" + uuid), env, var("sub_v1_" + uuid), depth + 1, maxdepth),
         (eval_expro, var("sub_e2_" + uuid), env, var("sub_v2_" + uuid), depth + 1, maxdepth),
         (sub, var("sub_v1_" + uuid), var("sub_v2_" + uuid), value)),
        ((eq, expr, ast.BinOp(left=var("mult_e1_" + uuid), op=ast.Mult(), right=var("mult_e2_" + uuid))),
         (typeo, var("mult_v1_" + uuid), int),
         (typeo, var("mult_v2_" + uuid), int),
         (eval_expro, var("mult_e1_" + uuid), env, var("mult_v1_" + uuid), depth + 1, maxdepth),
         (eval_expro, var("mult_e2_" + uuid), env, var("mult_v2_" + uuid), depth + 1, maxdepth),
         (mul, var("mult_v1_" + uuid), var("mult_v2_" + uuid), value)),
        ((eq, expr, ast.BinOp(left=var("mod_e1_" + uuid), op=ast.Mod(), right=var("mod_e2_" + uuid))),
         (eval_expro, var("mod_e1_" + uuid), env, var("mod_v1_" + uuid), depth + 1, maxdepth),
         (eval_expro, var("mod_e2_" + uuid), env, var("mod_v2_" + uuid), depth + 1, maxdepth),
         (mod, var("mod_v1_" + uuid), var("mod_v2_" + uuid), value)),

        # Functions
        ((eq, expr, ast.Call(func=var("func" + uuid), args=[], keywords=[])),
         (typeo, var("func_v" + uuid), FunctionType),
         (eval_expro, var("func" + uuid), env, var("func_v" + uuid), depth + 1, maxdepth),
         (callo, var("func_v" + uuid), value)),
        ((eq, expr, ast.Lambda(body=var("body" + uuid), args=[])),
         (typeo, value, FunctionType),
         (eval_expro, var("body" + uuid), env, var("body_v" + uuid), depth + 1, maxdepth),
         (eq, lambda: var("body_v" + uuid), value)),

        # Lists
        ((eq, expr, ast.List(elts=var("list_elements_" + uuid), ctx=ast.Load())),
         (eval_listo, var("list_elements_" + uuid), env, value, depth, maxdepth)),
        # ((eval_listo, expr, env, value, depth, maxdepth),)
    )
    # fmt: on


def eval_listo(exprs: Union[List, Var], env, value, depth=0, maxdepth=3):
    if depth >= maxdepth:
        # logger.debug("Depth {} reached, which is the maximum depth".format(depth))
        return fail
    uuid = str(uuid4())[:4]
    head_expr = var("head_expr_" + uuid)
    tail_expr = var("tail_expr_" + uuid)
    head_value = var("head_value_" + uuid)
    tail_value = var("tail_value_" + uuid)
    lcons_value = var("lcons_value" + uuid)
    return (conde,
        (# Either empty list or filled list
         # (conde,
         #  ((typeo, exprs, list),),
         #  ((typeo, exprs, LCons),)),
         # (conde,
         #  (typeo, value, list),
         #  (typeo, value, LCons),),
         (typeo, exprs, list),
         (typeo, value, list),
         (conde,
          ((eq, exprs, []),
           (eq, value, [])),
          ((conso, head_expr, tail_expr, exprs),
           (eval_expro, head_expr, env, head_value, depth + 1, maxdepth),
           # TODO: how to do depth in lists?
           (eval_listo, tail_expr, env, tail_value, depth + 0.5, maxdepth),
           # TODO: LCons is reified to a tuple, hence the extra step. Maybe make LCons nicer or get rid of LCons?
           (conso, head_value, tail_value, lcons_value),
           (callo, list, value, lcons_value),  # TODO: This is very ugly
          )))
    )


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
