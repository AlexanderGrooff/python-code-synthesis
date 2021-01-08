from kanren import run

from evalo.evalo import typeo
from unification import var

from tests.helpers import EvaloTestCase


class TestTypeo(EvaloTestCase):
    def test_typeo_correctly_parses_int(self):
        x = var()
        goals = typeo(1, x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], int)

    def test_typeo_correctly_parses_str(self):
        x = var()
        goals = typeo("bla", x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], str)

    def test_typeo_correctly_parses_tuple(self):
        x = var()
        goals = typeo((1, 2, 3), x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], tuple)

    def test_typeo_correctly_parses_list(self):
        x = var()
        goals = typeo([1, 2, 3], x)
        ret = run(1, x, goals)
        self.assertEqual(ret[0], list)
