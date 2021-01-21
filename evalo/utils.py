import ast
from copy import deepcopy
from typing import Union, Iterable, T, List

import astunparse
from loguru import logger
from unification import var


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
        try:
            return astunparse.unparse(obj).strip() if unparse else ast.dump(obj)
        except:
            return ast_dump_if_possible(obj)
    if isinstance(obj, dict):
        return {k: rec_ast_parse(v) for k, v in obj.items()}
    return [rec_ast_parse(a) for a in obj]


def ast_dump_if_possible(obj: T) -> Union[str, T]:
    if isinstance(obj, str):  # Str is also Iterable
        return obj
    if isinstance(obj, Iterable):
        return [ast_dump_if_possible(_) for _ in obj]
    if isinstance(obj, ast.AST):
        return ast.dump(obj)
    return obj


def get_ast_complexity(obj) -> int:
    if isinstance(obj, ast.AST):
        complexity = len(vars(obj))
        for c in vars(obj):
            complexity += get_ast_complexity(c)
        return complexity
    return 0


def sort_by_complexity(l: List[ast.AST]) -> List[ast.AST]:
    return sorted(l, key=lambda a: get_ast_complexity(a))


def strip_ast(obj: ast.AST) -> ast.AST:
    """
    Strip an AST object from all irrelevant attributes like lineno. Useful for stripping input from ast.parse.
    This does not mutate the original object because a new object is made.
    :param ast.AST obj: AST object
    :rtype: ast.AST
    """
    logger.debug("Stripping object {}".format(ast_dump_if_possible(obj)))
    new_obj = deepcopy(obj)
    for irrelevant_attr in [
        "type_ignores",
        "type_comment",
        "lineno",
        "col_offset",
        "end_lineno",
        "end_col_offset",
        "kind",
    ]:
        if hasattr(new_obj, irrelevant_attr):
            delattr(new_obj, irrelevant_attr)
            logger.debug(
                "Removed {} from {}".format(
                    irrelevant_attr, ast_dump_if_possible(new_obj)
                )
            )
    logger.debug("Stripping contents of {}".format(ast_dump_if_possible(new_obj)))
    for k, v in vars(new_obj).items():
        if isinstance(v, Iterable) and not isinstance(v, str):
            new_v = type(v)([strip_ast(c) for c in v if isinstance(c, ast.AST)])
        elif isinstance(v, ast.AST):
            new_v = strip_ast(v)
        else:
            new_v = v
        setattr(new_obj, k, new_v)
    logger.debug("Stripped object: {}".format(ast_dump_if_possible(new_obj)))
    return new_obj


def replace_ast_name_with_lvar(obj: ast.AST, replace_var: str) -> ast.AST:
    """
    Replace a name being loaded in the AST with a logic variable
    """
    if isinstance(obj, ast.Name) and obj.id == replace_var:
        return var(replace_var)

    new_obj = deepcopy(obj)
    for k, v in vars(obj).items():
        if isinstance(v, Iterable) and not isinstance(v, str):
            new_v = type(v)(
                [
                    replace_ast_name_with_lvar(c, replace_var)
                    for c in v
                    if isinstance(c, ast.AST)
                ]
            )
        elif isinstance(v, ast.AST):
            new_v = replace_ast_name_with_lvar(v, replace_var)
        else:
            new_v = v
        setattr(new_obj, k, new_v)
    return new_obj
