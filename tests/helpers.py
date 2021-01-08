from unittest import TestCase

from kanren import run, conde, lall

from evalo import eval_expro, ast_dump_if_possible
from evalo.evalo import eval_stmto


class EvaloTestCase(TestCase):
    def run_expr(self, expr, value, eval_expr=False, env=list(), existing_goals=list(), maxdepth=3, n=5):
        goals = eval_expro(expr, env, value, depth=0, maxdepth=maxdepth)
        if existing_goals:
            goals = conde((goals,), (existing_goals,))
        results = run(n, expr if eval_expr else value, goals)
        print(
            "Evaluated results: {}".format([ast_dump_if_possible(x) for x in results])
        )
        return results, goals

    def run_stmt(self, stmt, value, eval_expr=False, env=list()):
        goals, new_env = eval_stmto(stmt, env, value)
        results = run(5, stmt if eval_expr else value, goals)
        print("Evaluated results: {}".format(ast_dump_if_possible(list(results))))
        return results, goals, new_env
