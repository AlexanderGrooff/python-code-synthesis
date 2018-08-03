from kanren import eq, vars, conde, goalify, isvar
from kanren.core import EarlyGoalError
import ast

typeo = goalify(type)


def eq_obj(x, y):
    """ x > y """
    if not isvar(x) and not isvar(y):
        return eq(x.__dict__, y.__dict__)
    else:
        raise EarlyGoalError()


def evalo(expr, value):
    return eval_expro(expr, [], value)


def eval_expro(expr, env, value):
    x, y = vars(2)
    return conde(
        ((eq_obj, expr, ast.Num(n=value)),  # Numbers
         (typeo, value, int)),
    )
