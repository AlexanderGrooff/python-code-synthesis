from uuid import uuid4
from kanren import eq, vars, conde, goalify, isvar, var, run, unifiable
from kanren.core import EarlyGoalError, lallfirst, success, fail
from unification.more import unify_object
import ast

typeo = goalify(type)


def eq_obj(x, y):
    """ obj_x == obj_y """
    if not isvar(x) and not isvar(y):
        return conde(
            (eq, x.__dict__, y.__dict__),
            (eq, x, y)
        )
    else:
        raise EarlyGoalError()


def check_if_duplicate_call(call_args_1, call_args_2):
    if call_args_1 == call_args_2:
        print('Found unending recursive call with args {}'.format(call_args_1))
        return True


def evalo(expr, value):
    unifiable(ast.AST)
    return eval_expro(expr, [], value)


def eval_expro(expr, env, value, previous_args=None):
    duplicate = check_if_duplicate_call((expr, env, value), previous_args)
    if duplicate:
        return fail

    v1 = var('v1')
    print('Evaluating {} to {} with env {}'.format(expr, value, env))
    return conde(
        ((eq, expr, ast.Expr(value=v1)),  # Expressions
         eval_expro(v1, env, value, (expr, env, value))),
        ((eq, expr, ast.Num(n=value)),  # Numbers
         (typeo, value, int),
         (typeo, expr, ast.Num)),
    )
