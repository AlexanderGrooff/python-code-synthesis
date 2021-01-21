import ast
from operator import add, sub, mul, mod
from types import FunctionType
from typing import List, Union
from uuid import uuid4

from unification.core import isground

from kanren.constraints import ConstrainedState, neq, isinstanceo
from kanren.term import applyo
from loguru import logger
from kanren import eq, var, unifiable, membero, conde

from kanren.core import fail, run, lall, lany
from kanren.goals import heado, tailo, conso
from unification import reify, Var, isvar

from evalo.utils import ast_dump_if_possible, strip_ast, replace_ast_name_with_lvar

unifiable(ast.AST)
DEFAULT_REPLACE_VAR = "x"


def typeo(v, t):
    def typeo_goal(S: ConstrainedState):
        nonlocal v, t

        v_rf, t_rf = reify((v, t), S)
        isground_all = [isground(reified_value, S) for reified_value in [v_rf, t_rf]]
        if not all(isground_all):
            if not isground(t_rf, S):
                g = eq(type(v_rf), t_rf)
                yield from g(S)
            # TODO: What if v_rf is not yet grounded?
            else:
                # g = applyo(isinstance, v_rf, t_rf)
                yield S
        else:
            if type(v_rf) == t_rf:
                yield S

    return typeo_goal


def binopo(x, y, v, op):
    def isnumber(n):
        return isinstance(n, int) or isinstance(n, float)

    def binopo_goal(S: ConstrainedState):
        nonlocal x, y, v, op

        uuid = str(uuid4())[:4]
        t = var("type_" + uuid)
        x_rf, y_rf, v_rf, op_rf = reify((x, y, v, op), S)
        isground_all = [
            isground(reified_value, S) for reified_value in [x_rf, y_rf, v_rf, op_rf]
        ]
        if not all(isground_all):
            # We can only fix one LV at a time
            if len([uv for uv in isground_all if uv is False]) == 1:
                # TODO: Revop the other vars
                if not isground(v_rf, S):
                    try:
                        g = lall(
                            isinstanceo(x_rf, t),
                            isinstanceo(y_rf, t),
                            isinstanceo(v_rf, t),
                            eq(op_rf(x_rf, y_rf), v_rf),
                        )
                    except Exception as e:
                        logger.debug(
                            "Got exception during binop with args {}: {}".format(
                                [x_rf, y_rf, v_rf, op_rf], e
                            )
                        )
                        return
                    yield from g(S)
        else:
            # TODO: Why isnt this covered by the `typeo` goal?
            try:
                g = lall(
                    isinstanceo(x_rf, t),
                    isinstanceo(y_rf, t),
                    isinstanceo(v_rf, t),
                    eq(op_rf(x_rf, y_rf), v_rf),
                )
            except Exception as e:
                logger.debug(
                    "Got exception during ungrounded binop with args {}: {}".format(
                        [x_rf, y_rf, v_rf, op_rf], e
                    )
                )
                return
            yield from g(S)

    return binopo_goal


def evalo(program: ast.AST, value: Var, replace_var: str = None):
    replace_var = replace_var or DEFAULT_REPLACE_VAR
    if value.token != replace_var:
        raise RuntimeError("Value {} should have token {}".format(value, replace_var))

    program = strip_ast(program)
    program = replace_ast_name_with_lvar(program, replace_var=replace_var)

    goals, env = eval_programo(program, [], value)
    res = run(1, value, goals)

    r = res[0]
    logger.info("Final result: {}".format(ast_dump_if_possible(res)))
    if isvar(r):
        logger.info("No results found for {}: {}".format(value, r))
        return r
    logger.info(
        "Found {} to be {}".format(ast_dump_if_possible(value), ast_dump_if_possible(r))
    )
    # TODO: This only works on the last assign
    if isinstance(r, ast.Name):
        evaluated_value = literal_lookup(r.id, env)
        logger.info(
            "Found evaluated value {}".format(ast_dump_if_possible(evaluated_value))
        )
        return evaluated_value


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


def eval_programo(program: ast.Module, env, value):
    logger.info(
        "Evaluating program {} to {} with env {}".format(
            ast_dump_if_possible(program),
            ast_dump_if_possible(value),
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
        (eq(expr, ast.Lambda(body=var('body_' + uuid), args=[])),
         typeo(value, FunctionType),
         eval_expro(var('body_' + uuid), env, var('body_v_' + uuid), depth + 1, maxdepth),
         eq(lambda: var('body_v_' + uuid), value)),
        (eq(expr, ast.Call(func=var('func_' + uuid), args=[], keywords=[])),
         typeo(var('func_v_' + uuid), FunctionType),
         eval_expro(var('func_' + uuid), env, var('func_v_' + uuid), depth + 1, maxdepth),
         applyo(var('func_v_' + uuid), [], value)),
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


def literal_lookup(name, env):
    for k, v in env:
        if name == k:
            return v


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
