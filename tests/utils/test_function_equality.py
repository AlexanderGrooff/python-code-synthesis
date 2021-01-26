from unittest import TestCase

from evalo.utils import function_equality


class TestFunctionEquality(TestCase):
    def test_lambda_with_constants_are_equal(self):
        self.assertTrue(function_equality(lambda: 123, lambda: 123))

    def test_lambdas_with_different_constants_are_not_equal(self):
        self.assertFalse(function_equality(lambda: 123, lambda: 234))

    def test_lambdas_with_identical_body_but_different_args_are_not_equal(self):
        self.assertFalse(function_equality(lambda a: 123 + a, lambda b: 123 + b))

    def test_lambas_with_identical_body_and_args_are_equal(self):
        self.assertTrue(function_equality(lambda a: 123, lambda a: 123))

    def test_evaluated_binop_is_same_as_constant(self):
        self.assertTrue(function_equality(lambda: 1 + 1, lambda: 2))

    def test_functions_are_equal_with_same_body(self):
        def f():
            return 123

        def g():
            return 123

        self.assertTrue(function_equality(f, g))

    def test_functions_with_multiple_args_are_equal(self):
        def f(a, b, c):
            return 123 + a + b + c

        def g(a, b, c):
            return 123 + a + b + c

        self.assertTrue(function_equality(f, g))

    def test_functions_with_multiple_kwargs_are_equal(self):
        def f(a=1, b=2, c=3):
            return 123 + a + b + c

        def g(a=1, b=2, c=3):
            return 123 + a + b + c

        self.assertTrue(function_equality(f, g))
