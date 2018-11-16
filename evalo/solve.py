from functools import partial
from kanren import reify
from kanren.core import EarlyGoalError, earlyorder, interleave, unique, lany, \
    dicthash, run, lall, multihash, take, goaleval
from kanren.util import pprint
from unification.core import reify
from evalo.evalo import eval_expro
from evalo.reify import ast_dump_substitute, ast_dump_if_possible


def solve(n, expr, env, value, maxdepth=3):
    goals = eval_expro(expr, env, value, depth=0, maxdepth=maxdepth)
    results = map(partial(reify, expr), goaleval(lall(goals))({}))
    return take(n, unique(results, key=multihash))
