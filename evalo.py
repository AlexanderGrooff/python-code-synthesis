from kanren import eq, vars, conde, goalify, isvar, var, run
from kanren.core import EarlyGoalError
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


def children_typeo(l, t):
    """ type(x[n]) == t """
    if not isvar(l) and not isvar(t):
        eqs = []
        for c in l:
            eqs.append(typeo(c, t))
        return eqs
    else:
        raise EarlyGoalError()


def evalo(expr, value):
    return eval_expro(expr, [], value)


def eval_expro(expr, env, value):
    x, y = vars(2)
    return conde(
        ((eq_obj, expr, ast.Num(n=value)),  # Numbers
         (typeo, value, int)),
        ((eq_obj, expr, ast.Module(body=x)),  # Module
         (typeo, x, list),),
         #everyg(eval_expro, [(e, env, value) for e in x])),
        ((eq_obj, expr, ast.Expr(value=value)),),
        #((eq, expr, value),),
    )
