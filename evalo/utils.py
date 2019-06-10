from kanren import var, conde, eq
from kanren.core import EarlyGoalError, lall, success, fail
from kanren.goals import conso, LCons
from evalo.reify import ast_dump_substitute, ast_dump_if_possible


def count_goals(goals):
    num_goals = 0
    for g in goals:
        try:
            num_children = len(g)
            num_goals += count_goals(g)
        except TypeError:
            num_goals += 1
    return num_goals


def debugo(x):
    def f(s):
        print("Variable: {}, Substitute: {}".format(ast_dump_if_possible(x), ast_dump_substitute(s)))
        yield s
    return f


def listeqo(l1, l2):
    h1 = var()
    h2 = var()
    t1 = var()
    t2 = var()
    tl1 = var()
    tl2 = var()
    return (conde,
        ((conso, h1, t1, l1),
         (conso, h2, t2, l2),
         (tuple2listo, t1, tl1),
         (tuple2listo, t2, tl2),
         (eq, h1, h2),
         (listeqo, tl1, tl2)),
        ((eq, l1, []),
         (eq, l2, [])),
    )


def tuple2listo(t, l):
    if isinstance(t, tuple):
        return (eq, l, [x for x in t])
    elif isinstance(t, LCons):
        return (eq, l, t.as_list())
    elif isinstance(t, list):
        return (eq, l, t)
    # Raise for var and bad types
    else:
        return fail
