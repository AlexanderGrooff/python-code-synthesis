from functools import partial
from kanren import reify
from kanren.core import EarlyGoalError, earlyorder, interleave, unique, lany, \
    dicthash
from kanren.util import pprint
from evalo.reify import ast_dump_substitute, ast_dump_if_possible


def solve(n, x, goals):
    evaluated_goals = goaleval(goals)({})
    reifications = []
    for g in evaluated_goals:
        yield debug_reify(x, g)
    #reifications = map(partial(debug_reify, x), evaluated_goals)
    #return reifications


def debug_reify(x, s):
    print('Reifying {} in {}'.format(x, ast_dump_substitute(s)))
    return ast_dump_if_possible(reify(x, s))


def find_fixed_point(f, arg):
    """
    Repeatedly calls f until a fixed point is reached.
    This may not terminate, but should if you apply some eventually-idempotent
    simplification operation like evalt.
    """
    last, cur = object(), arg
    while last != cur:
        last = cur
        cur = f(cur)
        print('Finding fixed point {} vs {}\n'.format(pprint(last), pprint(cur)))
    return cur


def goaleval(goal):
    """ Expand and then evaluate a goal
    Idempotent
    See also:
       goalexpand
    """
    if callable(goal):  # goal is already a function like eq(x, 1)
        print('Goal is callable')
        return goal
    if isinstance(goal, tuple):  # goal is not yet evaluated like (eq, x, 1)
        try:
            print('Goal is tuple; finding fixed point')
            return find_fixed_point(evalt, goal)
        except Exception as e:
            raise EarlyGoalError(e)
    raise TypeError("Expected either function or tuple")


def evalt(t):
    """ Evaluate tuple if unevaluated
    >>> from kanren.util import evalt
    >>> add = lambda x, y: x + y
    >>> evalt((add, 2, 3))
    5
    >>> evalt(add(2, 3))
    5
    """

    if isinstance(t, tuple) and len(t) >= 1 and callable(t[0]):
        print('Evaluating tuple with function {}'.format(t[0]))
        return t[0](*t[1:])
    else:
        print('Cannot evaluate further: {}'.format(t))
        return t


def expand_and_evalt(t):
    if isinstance(t, tuple) and len(t) >= 1 and callable(t[0]):
        print('Evaluating children of {}: {}'.format(t[0], t[1:]))
        new_tuple = [t[0]]
        for i, c in enumerate(t[1:]):
            print("evaluating c {}: {}".format(i, c))
            try:
                new_tuple.append(expand_and_evalt(c))
            except Exception as e:
                print("Couldn't expand child {}: {}".format(i, e))
        print('Calling operator of tuple {}'.format(new_tuple))
        return new_tuple[0](*new_tuple[1:])
    else:
        print('Cannot expand {} further'.format(t))
        return t


def safe_conde(*goalseqs):
    """ Logical cond

    Goal constructor to provides logical AND and OR

    conde((A, B, C), (D, E)) means (A and B and C) or (D and E)
    Equivalent to the (A, B, C); (D, E) syntax in Prolog.

    See Also:
        lall - logical all
        lany - logical any
    """
    return (lany, ) + tuple((safe_lall, ) + tuple(gs) for gs in goalseqs)


def safe_lall(*goals):
    """ Logical all with goal reordering to avoid EarlyGoalErrors

    See also:
        EarlyGoalError
        earlyorder

    >>> from kanren import lall, membero
    >>> x = var('x')
    >>> run(0, x, lall(membero(x, (1,2,3)), membero(x, (2,3,4))))
    (2, 3)
    """
    return (safe_lallgreedy, ) + tuple(earlyorder(*goals))


def safe_lallgreedy(*goals):
    """ Logical all that greedily evaluates each goals in the order provided.

    Note that this may raise EarlyGoalError when the ordering of the
    goals is incorrect. It is faster than lall, but should be used
    with care.

    >>> from kanren import eq, run, membero
    >>> x, y = var('x'), var('y')
    >>> run(0, x, lallgreedy((eq, y, set([1]))), (membero, x, y))
    (1,)
    >>> run(0, x, lallgreedy((membero, x, y), (eq, y, {1})))  # doctest: +SKIP
    Traceback (most recent call last):
      ...
    kanren.core.EarlyGoalError
    """
    hashed_goals = str(goals)
    mem = {}
    if not goals:
        return success
    if len(goals) == 1:
        return goals[0]

    def allgoal(s):
        if hashed_goals in mem.keys() and mem[hashed_goals] == s:
            print("Already processed goals {} with substitute {}".format(goals, s))
            return fail
        else:
            mem[hashed_goals] = s
            print("Mem is now {}".format(mem))
        g = goaleval(reify(goals[0], s))
        return unique(
            interleave(goaleval(reify(
                (safe_lallgreedy, ) + tuple(goals[1:]), ss))(ss) for ss in g(s)),
            key=dicthash)

    return allgoal
