from unittest import TestCase

from codetransformer import Code
from kanren import run

from evalo import eval_expro, ast_dump_if_possible
from evalo.evalo import eval_stmto, init_evalo
from evalo.utils import function_equality


class EvaloTestCase(TestCase):
    def setUp(self):
        init_evalo()

    def assertFunctionEqual(self, f1, f2):
        if function_equality(f1, f2):
            return True
        else:
            c_f1 = Code.from_pyfunc(f1)
            c_f2 = Code.from_pyfunc(f2)

            raise AssertionError(
                "Functions not equal: instructions {} vs {}".format(
                    c_f1.instrs, c_f2.instrs
                )
            )

    def run_expr(self, *args, **kwargs):
        return self.run_eval(eval_func=eval_expro, *args, **kwargs)

    def run_stmt(self, *args, **kwargs):
        return self.run_eval(eval_func=eval_stmto, *args, **kwargs)

    def run_eval(
        self,
        ast_expr,
        value,
        eval_func=None,
        eval_expr=False,
        env=list(),
        maxdepth=3,
        n=5,
    ):
        goals = eval_func(ast_expr, env, value, depth=0, maxdepth=maxdepth)
        results = run(n, ast_expr if eval_expr else value, goals)
        print(
            "Evaluated results: {}".format([ast_dump_if_possible(x) for x in results])
        )
        return results, goals
