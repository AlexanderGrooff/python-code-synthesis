import ast
from kanren import reify
from unification.more import reify_object
from copy import deepcopy

def reify_ast(s):
    """
    Reify ast objects in s
    """
    objects = []
    for s_dict in s:
        for k,v in s_dict.items():
            s_without_k = deepcopy(s_dict)
            del s_without_k[k]
            print('Reifying {}:{} with {}'.format(k, v, s_without_k))
            try:
                o = reify_object(v, s_without_k)
            except AttributeError:
                o = reify(v, s_without_k)
            objects.append(o)
    return [ast_dump_if_possible(o) for o in objects]

def ast_dump_if_possible(a):
    if isinstance(a, ast.AST):
        return ast.dump(a)
    return a
