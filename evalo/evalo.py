from kanren import eq, vars, conde, goalify, isvar, var, run, unifiable
from kanren.core import EarlyGoalError
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


def eq_objo(u, v):
    """ Goal such that u == v
    See also:
        unify_object
    """

    def goal_eq(s):
        result = unify_object(u, v, s)
        if result is not False:
            yield result

    return goal_eq


def children_typeo(l, t):
    """ type(x[n]) == t """
    if not isvar(l) and not isvar(t):
        eqs = []
        for c in l:
            eqs.append(typeo(c, t))
        return eqs
    else:
        raise EarlyGoalError()


def _reify_object_dict(o, s):
    obj = object.__new__(type(o))
    d = reify(o.__dict__, s)
    if d == o.__dict__:
        return o
    obj.__dict__.update(d)
    return obj


def evalo(expr, value):
    unifiable(ast.AST)
    return eval_expro(expr, [], value)


def eval_expro(expr, env, value):
    x, y = vars(2)
    return conde(
        ((eq, expr, ast.Num(n=value)),  # Numbers
         (typeo, value, int),
         (typeo, expr, ast.Num)),
        ((eq_obj, expr, ast.Module(body=x)),  # Module
         (typeo, x, list),),
         #everyg(eval_expro, [(e, env, value) for e in x])),
        ((eq_obj, expr, ast.Expr(value=value)),),
        #((eq, expr, value),),
    )
