import ast
from kanren import var

from tests.helpers import EvaloTestCase


class TestStatements(EvaloTestCase):
    def test_expression_is_evaluated_to_value(self):
        ret, _, _ = self.run_stmt(ast.Expr(value=ast.Num(n=1)), var("expected_var"))
        self.assertEqual(ret[0], 1)

    # TODO: Fix this. Doesn't place var in env yet
    def test_assignment_adds_variable_to_env(self):
        _, goals, new_env = self.run_stmt(
            stmt=ast.Assign(
                targets=[ast.Name(id="a", ctx=ast.Store())],
                value=ast.Num(n=1),
            ),
            value=var("expected_var"),
            env=[],
        )
        self.assertIsInstance(new_env, list)
        self.assertEqual(new_env, [["a", 1]])
