import ast
from unittest import TestCase
from types import FunctionType
from kanren import var, run

from evalo.evalo import eval_expro


class TestExpressions(TestCase):
    def run_expr(self, expr, value, eval_expr=False, env=list()):
        results = run(5, expr if eval_expr else value, eval_expro(expr, env, value))
        print('Evaluated results: {}'.format([ast.dump(x) if isinstance(x, ast.AST) else x for x in results]))
        return results

    def test_number_value_results_in_ast_number(self):
        ret = self.run_expr(var(), 1, eval_expr=True)
        self.assertIsInstance(ret[0], ast.Num)

    def test_number_value_results_in_maximum_number_of_possibilities(self):
        ret = self.run_expr(var(), 1, eval_expr=True)
        self.assertEqual(len(ret), 5)

    def test_ast_addition_results_in_var_integer(self):
        ret = self.run_expr(ast.BinOp(left=ast.Num(n=1), op=ast.Add(), right=ast.Num(n=1)), var())
        self.assertEqual(ret[0], 2)

    def test_ast_subtraction_results_in_var_integer(self):
        ret = self.run_expr(ast.BinOp(left=ast.Num(n=1), op=ast.Sub(), right=ast.Num(n=1)), var())
        self.assertEqual(ret[0], 0)

    def test_ast_multiplication_results_in_var_integer(self):
        ret = self.run_expr(ast.BinOp(left=ast.Num(n=2), op=ast.Mult(), right=ast.Num(n=1)), var())
        self.assertEqual(ret[0], 2)

    # Float is not yet supported
    #def test_ast_division_results_in_var_integer(self):
    #    ret = self.run_expr(ast.Expr(value=ast.BinOp(left=ast.Num(n=2), op=ast.Div(), right=ast.Num(n=1))), var())
    #    self.assertEqual(ret[0], 1)

    def test_ast_modulo_results_in_var_integer(self):
        ret = self.run_expr(ast.BinOp(left=ast.Num(n=5), op=ast.Mod(), right=ast.Num(n=2)), var())
        self.assertEqual(ret[0], 1)

    def test_ast_string_results_in_var_string(self):
        ret = self.run_expr(ast.Str(s='Hello world!'), var())
        self.assertEqual(ret[0], 'Hello world!')

    def test_string_value_results_in_ast_string(self):
        ret = self.run_expr(var(), 'Hello world!', eval_expr=True)
        self.assertIsInstance(ret[0], ast.Str)
        self.assertEqual(ret[0].s, 'Hello world!')

    def test_ast_name_results_in_lookup_from_env(self):
        ret = self.run_expr(ast.Name(id='x', ctx=ast.Load()), var(), env=[['x', 1]])
        self.assertEqual(ret[0], 1)

    def test_ast_lambda_without_args_results_in_function_type(self):
        ret = self.run_expr(ast.Lambda(args=[], body=ast.Num(n=1)), var(), env=[])
        self.assertEqual(type(ret[0]), FunctionType)

    def test_ast_call_with_lambda_results_in_function_call(self):
        ret = self.run_expr(ast.Call(func=ast.Lambda(args=[], body=ast.Num(n=1)), args=[], keywords=[]), var(), env=[])
        self.assertEqual(ret[0], 1)
