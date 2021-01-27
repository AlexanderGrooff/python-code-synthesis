import ast

from evalo.evalo import evalo
from tests.helpers import EvaloTestCase


class TestEvalo(EvaloTestCase):
    def test_evaluate_expression_that_contains_the_replacevar(self):
        ret, _ = evalo(
            program=ast.parse("4"), exprs=[ast.parse("x")], values=[[]], replace_var="x"
        )
        self.assertTrue(len(ret) > 0)
        for r in ret:
            self.assertEqual(self.evaluate_ast_expr(r), [])

    def test_evaluate_assign_statement(self):
        ret, env = evalo(
            program=ast.parse("a = 1"),
            exprs=[ast.parse("x")],
            values=[4],
            replace_var="x",
        )
        self.assertTrue(len(ret) > 0)
        for r in ret:
            self.assertEqual(self.evaluate_ast_expr(r, env), 4)

    # TODO: This hangs
    # def test_no_results_are_given_if_constraints_are_impossible(self):
    #     ret = evalo(
    #         program=ast.parse("123"),
    #         exprs=[ast.parse("x"), ast.parse("x")],
    #         values=[1, 3],
    #         replace_var="x",
    #     )
    #     self.assertEqual(ret, ())

    def test_program_with_lambda(self):
        ret, _ = evalo(
            program=ast.parse("f = lambda: x"),
            exprs=[ast.parse("f()")],
            values=[[]],
            replace_var="x",
        )
        self.assertTrue(len(ret) > 0)
        for r in ret:
            self.assertEqual(self.evaluate_ast_expr(r), [])
