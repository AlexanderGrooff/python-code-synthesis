import ast
from unittest import TestCase
from kanren import var, run

from evalo.evalo import eval_stmto


class TestStatements(TestCase):
    def run_stmt(self, expr, value, eval_expr=False, env=list()):
        results = run(5, expr if eval_expr else value, eval_stmto(expr, env, value))
        print(
            "Evaluated results: {}".format(
                [ast.dump(x) if isinstance(x, ast.AST) else x for x in results]
            )
        )
        return results

    def test_expression_is_evaluated_to_value(self):
        ret = self.run_stmt(ast.Expr(value=ast.Num(n=1)), var("expected_var"))
        self.assertEqual(ret[0], 1)
