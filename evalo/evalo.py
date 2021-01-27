import ast
from operator import add, sub, mul, mod
from types import FunctionType
from typing import List, Union
from uuid import uuid4

from kanren.constraints import neq
from loguru import logger
from kanren import eq, var, unifiable, membero, conde

from kanren.core import fail, run, lall
from kanren.goals import heado, tailo, conso
from unification import Var, isvar

from evalo.goals import typeo, binopo, callo
from evalo.reify import init_reify
from evalo.unify import init_unify
from evalo.utils import (
    ast_dump_if_possible,
    strip_ast,
    replace_ast_name_with_lvar,
    print_divider_block,
    sort_by_complexity,
    module_to_expr,
)

DEFAULT_REPLACE_VAR = "x"


def init_evalo():
    unifiable(ast.AST)
    init_unify()
    init_reify()


def evalo(
    program: ast.AST, exprs: List[ast.AST], values: List, replace_var: Union[str, Var]
):
    replace_var = replace_var.token if isvar(replace_var) else replace_var
    globals()[replace_var] = var(replace_var)

    program = strip_ast(program)
    stripped_exprs = []
    for e in exprs:
        if isinstance(e, ast.Module):
            e = module_to_expr(e)
        e = strip_ast(e)
        e = replace_ast_name_with_lvar(e, replace_var=replace_var)
        stripped_exprs.append(e)
    exprs = stripped_exprs

    program = replace_ast_name_with_lvar(program, replace_var=replace_var)

    program_goals, env = eval_programo(program, [])

    expr_goals = []
    print_divider_block("Done parsing program")
    for expr, value in zip(exprs, values):
        logger.info("Evaluating {} with env {} to value {}".format(expr, env, value))
        g = eval_expro(expr, env, value)
        expr_goals.append(g)
        print_divider_block(f"Done parsing expr {expr}")

    results = run(3, globals()[replace_var], lall(program_goals, *expr_goals))
    return sort_by_complexity(results), env


def find_new_env_after_stmt(goals, old_env, new_env_lv):
    new_env_results = run(1, new_env_lv, goals)
    if not new_env_results:
        evaluated_env = old_env
    else:
        evaluated_env = new_env_results[0]
        if isvar(new_env_results[0]):
            logger.info(
                "Env has to be ground. Using old env {} instead of new env {}".format(
                    old_env, new_env_lv
                )
            )
            evaluated_env = old_env
        else:
            logger.info("Found new env {}".format(evaluated_env))
    logger.info("Returning new env {}".format(goals, evaluated_env))
    return evaluated_env


def eval_programo(program: ast.Module, env):
    logger.info(
        "Evaluating program {} with env {}".format(
            ast_dump_if_possible(program),
            ast_dump_if_possible(env),
        )
    )

    goals = []
    curr_env = env
    for ast_expr in program.body:
        logger.info(
            "Evaluating statement {} with env {}".format(
                ast_dump_if_possible(ast_expr), ast_dump_if_possible(curr_env)
            )
        )
        new_env = var()
        g = eval_stmto(ast_expr, curr_env, new_env)
        curr_env = find_new_env_after_stmt(g, old_env=curr_env, new_env_lv=new_env)
        goals.append(g)

    return conde(goals), curr_env


def eval_stmto(stmt, env, new_env, depth=0, maxdepth=3):
    logger.info(
        "Evaluating stmt {} to new env {} using old env {}".format(
            ast_dump_if_possible(stmt),
            ast_dump_if_possible(new_env),
            ast_dump_if_possible(env),
        )
    )
    if depth >= maxdepth:
        return fail

    uuid = str(uuid4())[:4]

    # fmt: off
    goals = conde(
        (eq(stmt, ast.Assign(targets=var('assign_targets_' + uuid), value=var("assign_value_" + uuid))),
         # TODO: Allow for multiple assigns: a, b, = ...
         heado(ast.Name(id=var('assign_lhs_' + uuid), ctx=ast.Store()), var('assign_targets_' + uuid)),
         eval_expro(var("assign_value_" + uuid), env, var("assign_rhs_" + uuid)),
         conso([var("assign_lhs_" + uuid), var("assign_rhs_" + uuid)], env, new_env),  # new_env = [lhs, rhs] + env
         ),
        # Expression statements don't change the environment
        (eq(stmt, ast.Expr(value=var("exprbody" + uuid))),  # Expressions
         eq(env, new_env)),
    )
    # fmt: on
    return goals


def eval_expro(expr, env, value, depth=0, maxdepth=3):
    # logger.debug("Evaluating expr {} to {} with env {}".format(expr, value, env))
    uuid = str(uuid4())[:4]
    if isinstance(expr, ast.AST):
        logger.info("Found AST for expr -> {}".format(ast_dump_if_possible(expr)))
    if isinstance(value, ast.AST):
        logger.info("Found AST for value -> {}".format(ast_dump_if_possible(value)))

    if depth >= maxdepth:
        return fail

    # Define function vars here so that they are easily reified with codetransformer
    body_v = var("body_v")  # TODO: Not so nice. This can overlap with other body_v's!

    # fmt: off
    return conde(
        (eq(expr, ast.Name(id=var('name_' + uuid), ctx=ast.Load())),
         lookupo(var('name_' + uuid), env, value)),
        # (lany(
        #     typeo(value, int),
        #     typeo(value, str),
        #  ),
        #  eq(expr, ast.Constant(value=value)),),
        (eq(expr, ast.Str(s=var('str_e_' + uuid))),
         typeo(value, str),
         eq(var('str_e_' + uuid), value)),
        (eq(expr, ast.Num(n=value)),
         membero(value, [_ for _ in range(5)])),
        (eq(expr, ast.BinOp(left=var('e1_' + uuid), op=var('op_e_' + uuid), right=var('e2_' + uuid))),
         typeo(var('v1_' + uuid), int),
         typeo(var('v2_' + uuid), int),
         eval_expro(var('e1_' + uuid), env, var('v1_' + uuid), depth + 1, maxdepth),
         eval_expro(var('e2_' + uuid), env, var('v2_' + uuid), depth + 1, maxdepth),
         eval_opo(var('op_e_' + uuid), var('op_v_' + uuid), var('v1_' + uuid), var('v2_' + uuid), value),
         binopo(var('v1_' + uuid), var('v2_' + uuid), value, op=var('op_v_' + uuid))),

        # Lists
        (eq(expr, ast.List(elts=var("list_elements_" + uuid), ctx=ast.Load())),
         eval_expr_listo(var("list_elements_" + uuid), env, value, depth, maxdepth)),

        # Functions
        (eq(expr, ast.Lambda(body=var('body_' + uuid), args=var("lambda_args_" + uuid))),
         typeo(value, FunctionType),
         eval_argso(var("lambda_args_" + uuid), env, var("lambda_lhs_" + uuid)),
         eval_expro(var('body_' + uuid), env, body_v, depth + 1, maxdepth),
         # TODO: How to do multiple args here?
         eq(lambda: body_v, value)),
        (eq(expr, ast.Call(func=var('func_' + uuid), args=[], keywords=[])),
         typeo(var('func_v_' + uuid), FunctionType),
         eval_expro(var('func_' + uuid), env, var('func_v_' + uuid), depth + 1, maxdepth),
         callo(var('func_v_' + uuid), [], value)),
    )
    # fmt: on


def eval_argso(args_expr, env, value):
    uuid = str(uuid4())[:4]
    args = var("args_" + uuid)
    # fmt: off
    return conde(
        (conde(
          # py38
          (eq(args_expr, ast.arguments(posonlyargs=[], args=args, vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])),),
          # py37
          (eq(args_expr, ast.arguments(args=args, vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])),),
          (eq(args_expr, []),)),
         eq(args, []),),
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


def eval_expr_listo(exprs: Union[List, Var], env, value, depth=0, maxdepth=3):
    """ Evaluate a list of expressions. Not the same as evaluating the List AST """
    if depth >= maxdepth:
        # logger.debug("Depth {} reached, which is the maximum depth".format(depth))
        return fail
    uuid = str(uuid4())[:4]
    head_expr = var("head_expr_" + uuid)
    tail_expr = var("tail_expr_" + uuid)
    head_value = var("head_value_" + uuid)
    tail_value = var("tail_value_" + uuid)
    # fmt: off
    return conde(
        (typeo(exprs, list),
         typeo(value, list),
         # Either empty list or filled list
         conde(
             (eq(exprs, []),
              eq(value, [])),
             (conso(head_expr, tail_expr, exprs),
              eval_expro(head_expr, env, head_value, depth + 1, maxdepth),
              # TODO: how to do depth in lists?
              typeo(tail_expr, list),
              typeo(tail_value, list),
              eval_expr_listo(tail_expr, env, tail_value, depth + 1, maxdepth),
              conso(head_value, tail_value, value))))
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
