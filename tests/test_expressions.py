import ast
from unittest import TestCase
from kanren import var, run

from evalo.evalo import evalo


class TestExpressions(TestCase):
    def run_expr(self, expr, value, eval_expr=False):
        results = run(2, expr if eval_expr else value, evalo(expr, value))
        print('Evaluated results: {}'.format([ast.dump(x) if isinstance(x, ast.AST) else x for x in results]))
        return results

    def test_expression_is_evaluated_to_value(self):
        ret = self.run_expr(ast.Expr(value=ast.Num(n=1)), var('expected_var'))
        self.assertEqual(ret[0], 1)

    def test_number_value_results_in_ast_number(self):
        ret = self.run_expr(var(), 1, eval_expr=True)
        self.assertIsInstance(ret[0], ast.Expr)
        self.assertIsInstance(vars(ret[0])['value'], ast.Num)

    def test_ast_addition_results_in_var_integer(self):
        ret = self.run_expr(ast.Expr(value=ast.BinOp(left=ast.Num(n=1), op=ast.Add(), right=ast.Num(n=1))), var())
        self.assertEqual(ret[0], 2)
