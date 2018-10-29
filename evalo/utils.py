from kanren.core import success
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
