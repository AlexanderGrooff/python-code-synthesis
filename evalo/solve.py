from functools import partial
from typing import Hashable
from unittest.mock import patch

from kanren.core import unique, lall, multihash, take, goaleval, success, lallgreedy
from kanren.util import interleave, dicthash
from unification.core import reify, unify
from evalo.evalo import eval_expro
import multiprocessing_on_dill as mp


PREFETCH_AMOUNT = 5
POOL = mp.Pool(16)


def m_eq(u, v):
    """ Goal such that u == v

    See also:
        unify
    """

    def goal_eq(s):
        result = unify(u, v, s)
        if result is not False:
            return result

    return goal_eq


def m_unique(seq, key):
    print("Getting unique from {}".format(seq))
    seen = set()
    for item in seq:
        try:
            k = key(item)
        except TypeError:
            # Just yield it and hope for the best, since we can't efficiently
            # check if we've seen it before.
            yield item
            continue
        if not isinstance(k, Hashable):
            # Just yield it and hope for the best, since we can't efficiently
            # check if we've seen it before.
            yield item
        elif k not in seen:
            seen.add(key(item))
            yield item


def m_interleave(seqs, pass_exceptions=()):
    print("Interleaving these sequences {}".format(seqs))
    iters = map(iter, seqs)
    while iters:
        newiters = []
        for itr in iters:
            try:
                yield next(itr)
                newiters.append(itr)
            except (StopIteration, ) + tuple(pass_exceptions):
                pass
        iters = newiters


def m_lallgreedy(*goals):
    if not goals:
        return success
    if len(goals) == 1:
        return goals[0]

    def allgoal(s):
        print("Running all goals")
        g = goaleval(reify(goals[0], s))

        def prefetch(ss):
            g = goaleval(reify((lallgreedy, ) + tuple(goals[1:]), ss))(ss)
            res = []
            for i in range(PREFETCH_AMOUNT):
                try:
                    res.append(next(g))
                except StopIteration:
                    break
            return res

        res = POOL.map(prefetch, g(s))
        print(res)

        return m_unique(
            m_interleave(goaleval(reify(
                (lallgreedy, ) + tuple(goals[1:]), ss))(ss) for ss in g(s)),
            key=dicthash)

    return allgoal


@patch('kanren.core.unique', m_unique)
@patch('kanren.core.interleave', m_interleave)
@patch('kanren.core.eq', m_eq)
@patch('kanren.core.lallgreedy', m_lallgreedy)
def solve(n, expr, env, value, maxdepth=3):
    goals = eval_expro(expr, env, value, depth=0, maxdepth=maxdepth)
    results = map(partial(reify, expr), goaleval(lall(goals))({}))
    return take(n, unique(results, key=multihash))


def multisolve(n, expr, env, value, maxdepth=3):
    print("Creating goals")
    goals = eval_expro(expr, env, value, depth=0, maxdepth=maxdepth)
    print("Goals found: {}".format(len(goals)))
    goal_evaluator = goaleval(lall(goals))
    print("Created goalevaluator: {}".format(goal_evaluator))

    evaluated_goals = take(n, goal_evaluator({}))
    print("Evaluated goals: {}".format(evaluated_goals))
    results = list(map(partial(reify, expr), evaluated_goals))
    print("Mapped results: {}".format(results))
    return take(n, unique(results, key=multihash))
