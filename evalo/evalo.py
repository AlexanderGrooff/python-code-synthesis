from uuid import uuid4
from kanren import eq, vars, conde, goalify, isvar, var, run, unifiable
from kanren.arith import add
from kanren.core import EarlyGoalError, lallfirst, success, fail
from unification.more import unify_object
import ast

typeo = goalify(type)


def check_if_duplicate_call(call_args_1, call_args_2):
    if call_args_1 == call_args_2:
        print('Found unending recursive call with args {}'.format(call_args_1))
        return True


def evalo(program, value):
    unifiable(ast.AST)
    return eval_programo(program, [], value)


def eval_programo(program, env, value, previous_args=None):
    print('Evaluating program {} to {} with env {}'.format(program, value, env))
    current_args = (program, env, value)
    duplicate = check_if_duplicate_call(current_args, previous_args)
    if duplicate:
        return fail

    return conde(
        ((eval_stmto, program, env, value, previous_args),),  # Change this
    )


def eval_stmto(stmt, env, value, previous_args=None):
    print('Evaluating stmt {} to {} with env {}'.format(stmt, value, env))
    current_args = (stmt, env, value)
    duplicate = check_if_duplicate_call(current_args, previous_args)
    if duplicate:
        return fail

    exprbody = var('exprbody')
    return conde(
        ((eq, stmt, ast.Expr(value=exprbody)),  # Expressions
         (eval_expro, exprbody, env, value)),
    )


def eval_expro(expr, env, value, previous_args=None):
    print('Evaluating expr {} to {} with env {}'.format(expr, value, env))
    current_args = (expr, env, value)
    duplicate = check_if_duplicate_call(current_args, previous_args)
    if duplicate:
        return fail

    op = var('op')
    v1 = var('v1')
    v2 = var('v2')
    e1 = var('e1')
    e2 = var('e2')
    return conde(
        ((eq, expr, ast.Num(n=value)),),  # Numbers
        ((eq, expr, ast.BinOp(left=v1, op=op, right=v2)),  # Expressions
         (add, e1, e2, value),
         (eq, op, ast.Add()),
         (eval_expro, v1, env, e1, current_args),
         (eval_expro, v2, env, e2, current_args)),
    )
