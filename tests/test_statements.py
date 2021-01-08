import ast
from kanren import var
from unification import Var

from tests.helpers import EvaloTestCase


class TestStatements(EvaloTestCase):
    def test_expression_is_evaluated_to_value(self):
        ret, _, _ = self.run_stmt(ast.Expr(value=ast.Num(n=1)), var("expected_var"))
        self.assertEqual(ret[0], 1)

    def test_assignment_adds_variable_to_env(self):
        _, goals, new_env = self.run_stmt(
            stmt=ast.Assign(
                targets=[ast.Name(id="a", ctx=ast.Store())],
                value=ast.Num(n=3),
            ),
            value=var("expected_var"),
            env=[],
        )
        self.assertIsInstance(new_env, Var)
        # ret, _ = self.run_expr(expr=new_env, value=var(), env=new_env, existing_goals=goals)
        ret, _ = self.run_expr(
            expr=ast.Name(id="a", ctx=ast.Load()), value=var(), existing_goals=goals
        )
        self.assertEqual(ret[0], [["a", 3]])
