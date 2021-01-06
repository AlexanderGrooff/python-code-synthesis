from kanren import reify
from unification.more import reify_object
from copy import deepcopy

from evalo.utils import rec_ast_parse


def reify_ast(s):
    """
    Reify ast objects in s
    """
    for s_dict in s:
        for k, v in s_dict.items():
            s_without_k = deepcopy(s_dict)
            print(
                "Reifying {}:{} with {}".format(
                    k, rec_ast_parse(v), rec_ast_parse(s_without_k)
                )
            )
            try:
                v = reify_object(v, s_without_k)
                print("Reified object {}".format(k))
            except AttributeError:
                v = reify(v, s_without_k)
            s_dict[k] = v
            print("Reified {} to {}".format(k, rec_ast_parse(v), s_without_k))
    return s
