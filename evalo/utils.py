import ast
from typing import Union, Iterable, T

import astunparse


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
        print("Variable: {}, Substitute: {}".format(rec_ast_parse(x), rec_ast_parse(s)))
        yield s

    return f


def rec_ast_parse(obj: Union[ast.AST, Iterable], unparse=True):
    if isinstance(obj, ast.AST):
        return astunparse.unparse(obj).strip() if unparse else ast.dump(obj)
    if isinstance(obj, dict):
        return {k: rec_ast_parse(v) for k, v in obj.items()}
    return [rec_ast_parse(a) for a in obj]


def ast_dump_if_possible(obj: T) -> Union[str, T]:
    if isinstance(obj, ast.AST):
        return ast.dump(obj)
    return obj
