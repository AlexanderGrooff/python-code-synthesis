from functools import partial
from kanren.core import unique, lall, multihash, take, goaleval
from unification.core import reify
from evalo.evalo import eval_expro


def solve(n, expr, env, value, maxdepth=3):
    goals = eval_expro(expr, env, value, depth=0, maxdepth=maxdepth)
    results = map(partial(reify, expr), goaleval(lall(goals))({}))
    return take(n, unique(results, key=multihash))
