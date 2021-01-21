from unittest import TestCase

from kanren import run, conde, lall

from evalo import eval_expro, ast_dump_if_possible
from evalo.evalo import eval_stmto


class EvaloTestCase(TestCase):
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
