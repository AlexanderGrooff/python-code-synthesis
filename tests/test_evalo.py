import ast

from kanren import run
from unification import var

from evalo.evalo import evalo
from tests.helpers import EvaloTestCase


class TestEvalo(EvaloTestCase):
    def test_single_statement_is_evaluated(self):
        x = var()
        goals = evalo(ast.parse("x = []"), x)
        r = run(1, x, goals)
        self.assertEqual(r[0], [])

    def test_multiple_statements_are_handled(self):
        x = var()
        goals = evalo(ast.parse("[]; x = []"), x)
        r = run(1, x, goals)
        self.assertEqual(r[0], [])

    def test_env_is_used_for_next_statement(self):
        x = var()
        goals = evalo(ast.parse("a = []; x = a"), x)
        r = run(1, x, goals)
        self.assertEqual(r[0], [])
