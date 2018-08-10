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
            #del s_without_k[k]
            print('Reifying {}:{} with {}'.format(k, ast_dump_if_possible(v),
                  ast_dump_substitute(s_without_k)))
            try:
                v = reify_object(v, s_without_k)
                print('Reified object {}'.format(k))
            except AttributeError:
                v = reify(v, s_without_k)
            s_dict[k] = v
            print('Reified {} to {}'.format(k, ast_dump_if_possible(v),
                  s_without_k))
    return s

def ast_dump_if_possible(a):
    if isinstance(a, ast.AST):
        return ast.dump(a)
    return a

def ast_dump_substitute(s):
    return {k: ast_dump_if_possible(v) for k,v in s.items()}
