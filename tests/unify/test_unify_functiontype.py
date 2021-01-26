from unification import var, unify

from tests.helpers import EvaloTestCase


class TestUnifyFunctionType(EvaloTestCase):
    def test_unify_identical_functions_results_in_empty_dict(self):
        self.assertEqual(unify(lambda: 123, lambda: 123, {}), {})

    def test_mismatching_functions_return_false(self):
        self.assertEqual(unify(lambda: 123, lambda: 234, {}), False)

    def test_body_is_unified(self):
        x = var("x")
        self.assertEqual(unify(lambda: 123, lambda: x, {}), {x: 123})
