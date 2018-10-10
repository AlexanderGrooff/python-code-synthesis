from functools import partial
from kanren import reify
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
        print('Cannot evaluate tuple {}'.format(t))
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
        print('Cannot evaluate {} further'.format(t))
        return t
