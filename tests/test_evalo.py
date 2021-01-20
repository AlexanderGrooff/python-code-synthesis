import ast

from unification import var

from evalo.evalo import evalo
from tests.helpers import EvaloTestCase


class TestEvalo(EvaloTestCase):
    def test_single_statement_is_evaluated(self):
        x = var("x")
        r = evalo(ast.parse("x = []"), x)
        self.assertEqual(r[0], [])

    def test_other_replacevar_can_be_specified(self):
        x = var("a")
        r = evalo(ast.parse("a = []"), x, replace_var="a")
        self.assertEqual(r[0], [])

    def test_multiple_statements_are_handled(self):
        x = var("x")
        r = evalo(ast.parse("[]; x = []"), x)
        self.assertEqual(r[0], [])

    def test_env_is_used_for_next_statement(self):
        x = var("x")
        r = evalo(ast.parse("a = []; x = a"), x)
        self.assertEqual(r[0], [])

    def test_assigning_a_different_variable_doesnt_create_results(self):
        x = var("x")
        # Specific replace_var to make example clearer
        r = evalo(ast.parse("a = []"), x, replace_var="x")
        # Result is just the logic var
        self.assertEqual(r[0], x)
