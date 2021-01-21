import ast
from kanren import var

from tests.helpers import EvaloTestCase


class TestStatements(EvaloTestCase):
    def test_expression_doesnt_change_env(self):
        ret, _ = self.run_stmt(ast_expr=ast.Expr(value=ast.Num(n=1)), value=var())
        self.assertEqual(ret[0], [])

    def test_assignment_adds_variable_to_env(self):
        ret, _ = self.run_stmt(
            ast_expr=ast.Assign(
                targets=[ast.Name(id="a", ctx=ast.Store())],
                value=ast.Num(n=1),
            ),
            value=var(),
            env=[],
        )
        self.assertEqual(ret[0], [["a", 1]])

    def test_reverse_interpret_assignment(self):
        ret, _ = self.run_stmt(
            ast_expr=ast.Assign(
                targets=[ast.Name(id="a", ctx=ast.Store())],
                value=var(),
            ),
            value=[["a", []]],
            env=[],
            eval_expr=True,
        )
        self.assertIsInstance(ret[0], ast.Assign)
        self.assertEqual(ast.literal_eval(ret[0].value), [])
