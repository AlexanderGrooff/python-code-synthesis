import ast
from kanren import var

from evalo.utils import strip_ast
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

    def test_assignment_puts_lambda_in_env(self):
        a = strip_ast(ast.parse("f = lambda: []"))
        ret, _ = self.run_stmt(
            ast_expr=a.body[0],
            value=var(),
            env=[],
        )
        self.assertEqual(ret[0][0][0], "f")
        self.assertEqual(ret[0][0][1](), [])
