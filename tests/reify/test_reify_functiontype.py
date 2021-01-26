from unification import reify, var

from tests.helpers import EvaloTestCase


global_lv = var("global_lv")
global_val = 234


class TestReifyFunctionType(EvaloTestCase):
    def test_lambda_reifies_without_lvs(self):
        self.assertFunctionEqual(reify(lambda: 123, {}), lambda: 123)

    def test_lambda_reifies_lv_into_lambda(self):
        x = var("x")
        self.assertFunctionEqual(reify(lambda: x, {x: 234}), lambda: 234)

    def test_lambda_is_not_reified_if_var_is_unknown(self):
        x = var("x")
        self.assertFunctionEqual(reify(lambda: x, {}), lambda: x)

    # TODO: This shouldn't be necessary
    def test_lambda_needs_to_have_named_lv(self):
        x = var()
        self.assertFunctionEqual(reify(lambda: x, {x: 123}), lambda: x)

    def test_lambda_reifies_global_var(self):
        self.assertFunctionEqual(
            reify(lambda: global_lv, {global_lv: 123}), lambda: 123
        )

    def test_lambda_reifies_global_val(self):
        self.assertFunctionEqual(reify(lambda: global_val, {}), lambda: global_val)

    def test_lambda_reifies_global_var_to_global_val(self):
        self.assertFunctionEqual(
            reify(lambda: global_lv, {global_lv: global_val}), lambda: 234
        )
