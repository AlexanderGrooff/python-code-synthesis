import ast
from unittest import TestCase
from kanren import var, run

from evalo import evalo


class TestExpressions(TestCase):
    def run_expr(self, expr, value, eval_expr=False):
        results = run(0, expr if eval_expr else value, evalo(expr, value))
        print('Evaluated results: {}'.format(results))
        return results

    def test_number_ast_results_in_var_integer(self):
        ret = self.run_expr(ast.Num(n=1), var())
        self.assertEqual(ret[0], 1)

    def test_number_value_results_in_ast_number(self):
        ret = self.run_expr(var(), 1, eval_expr=True)
        self.assertEqual(ret[0], ast.Num(n=1))
