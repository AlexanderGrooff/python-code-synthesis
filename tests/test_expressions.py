import ast
from types import FunctionType
from kanren import var

from tests.helpers import EvaloTestCase


class TestExpressions(EvaloTestCase):
    def test_number_value_results_in_ast_number(self):
        ret, _ = self.run_expr(var(), 1, eval_expr=True)
        self.assertIsInstance(ret[0], ast.Num)

    def test_number_value_results_in_maximum_number_of_possibilities(self):
        ret, _ = self.run_expr(var(), 1, eval_expr=True)
        self.assertEqual(len(ret), 5)

    def test_asts_can_be_partially_filled_in(self):
        ret, _ = self.run_expr(
            ast.BinOp(left=ast.Num(n=1), op=ast.Add(), right=ast.Num(n=var())),
            3,
            eval_expr=True,
        )
        self.assertEqual(ret[0].right.n, 2)

    def test_ast_addition_results_in_var_integer(self):
        ret, _ = self.run_expr(
            ast.BinOp(left=ast.Num(n=1), op=ast.Add(), right=ast.Num(n=1)), var()
        )
        self.assertEqual(ret[0], 2)

    def test_ast_subtraction_results_in_var_integer(self):
        ret, _ = self.run_expr(
            ast.BinOp(left=ast.Num(n=1), op=ast.Sub(), right=ast.Num(n=1)), var()
        )
        self.assertEqual(ret[0], 0)

    def test_ast_multiplication_results_in_var_integer(self):
        ret, _ = self.run_expr(
            ast.BinOp(left=ast.Num(n=2), op=ast.Mult(), right=ast.Num(n=1)), var()
        )
        self.assertEqual(ret[0], 2)

    # Float is not yet supported
    # def test_ast_division_results_in_var_integer(self):
    #    ret, _ = self.run_expr(ast.Expr(value=ast.BinOp(left=ast.Num(n=2), op=ast.Div(), right=ast.Num(n=1))), var())
    #    self.assertEqual(ret[0], 1)

    def test_ast_modulo_results_in_var_integer(self):
        ret, _ = self.run_expr(
            ast.BinOp(left=ast.Num(n=3), op=ast.Mod(), right=ast.Num(n=2)), var()
        )
        self.assertEqual(ret[0], 1)

    def test_ast_modulo_with_rhs_zero_is_not_picked_up(self):
        ret, _ = self.run_expr(
            ast.BinOp(left=ast.Num(n=3), op=ast.Mod(), right=ast.Num(n=0)), var()
        )
        self.assertEqual(len(ret), 0)

    def test_ast_string_results_in_var_string(self):
        ret, _ = self.run_expr(ast.Str(s="Hello world!"), var())
        self.assertEqual(ret[0], "Hello world!")

    # TODO: n=1 because otherwise it's very slow. Not sure why
    def test_string_value_results_in_ast_string(self):
        ret, _ = self.run_expr(var(), "Hello world!", eval_expr=True, n=1)
        self.assertIn(type(ret[0]), [ast.Str, ast.Constant])  # Can be Constant in 3.8+
        self.assertEqual(ret[0].s, "Hello world!")

    def test_ast_name_results_in_lookup_from_env(self):
        ret, _ = self.run_expr(ast.Name(id="x", ctx=ast.Load()), var(), env=[["x", 1]])
        self.assertEqual(ret[0], 1)

    def test_ast_lambda_without_args_results_in_function_type(self):
        ret, _ = self.run_expr(ast.Lambda(args=[], body=ast.Num(n=1)), var(), env=[])
        self.assertEqual(type(ret[0]), FunctionType)

    def test_ast_call_with_lambda_results_in_function_call(self):
        ret, _ = self.run_expr(
            ast.Call(func=ast.Lambda(args=[], body=ast.Num(n=1)), args=[], keywords=[]),
            var(),
            env=[],
        )
        self.assertEqual(ret[0], 1)

    def test_ast_empty_list_evaluates_to_empty_list(self):
        ret, goals = self.run_expr(
            ast_expr=ast.List(elts=[], ctx=ast.Load()),
            value=var(),
        )
        self.assertEqual(ret[0], [])

    def test_ast_single_element_list_is_correctly_interpreted(self):
        ret, _ = self.run_expr(
            ast_expr=ast.List(elts=[ast.Num(n=1)], ctx=ast.Load()),
            value=var(),
            maxdepth=4,
        )
        self.assertEqual(ret[0], [1])

    def test_ast_multiple_element_list_is_correctly_interpreted(self):
        ret, _ = self.run_expr(
            ast_expr=ast.List(elts=[ast.Num(n=1), ast.Num(n=3)], ctx=ast.Load()),
            value=var(),
            maxdepth=4,
        )
        self.assertEqual(ret[0], [1, 3])

    def test_ast_nested_list_is_correctly_interpreted(self):
        ret, _ = self.run_expr(
            ast_expr=ast.List(
                elts=[ast.Num(n=2), ast.List(elts=[ast.Num(n=1)], ctx=ast.Load())],
                ctx=ast.Load(),
            ),
            value=var(),
            maxdepth=4,
        )
        self.assertEqual(ret[0], [2, [1]])

    def test_empty_list_can_be_reverse_interpreted(self):
        ret, _ = self.run_expr(var(), [], eval_expr=True, n=3)
        for r in ret:
            v, _ = self.run_expr(r, var(), n=1)
            self.assertEqual(v[0], [])

    def test_filled_list_can_be_reverse_interpreted(self):
        ret, _ = self.run_expr(var(), [1], eval_expr=True, n=3)
        for r in ret:
            v, _ = self.run_expr(r, var(), n=1)
            self.assertEqual(v[0], [1])
