from kanren import run
from unification import var

from evalo.evalo import lookupo
from tests.helpers import EvaloTestCase


class TestLookupo(EvaloTestCase):
    def test_lookupo_doesnt_return_anything_if_name_not_in_env(self):
        x = var()
        ret = run(1, x, lookupo("a", [], x))
        self.assertEqual(len(ret), 0)

    def test_match_is_returned(self):
        x = var()
        ret = run(1, x, lookupo("a", [["a", 1]], x))
        self.assertEqual(ret[0], 1)

    def test_first_match_is_returned(self):
        x = var()
        ret = run(1, x, lookupo("a", [["a", 1], ["a", 2]], x))
        self.assertEqual(ret[0], 1)

    # TODO: Not sure if we want this kind of behaviour
    def test_reverse_interpret_to_the_last_name_added_to_env(self):
        x = var()
        ret = run(1, x, lookupo(x, [["a", 1], ["b", 1]], 1))
        self.assertEqual(ret[0], "a")
