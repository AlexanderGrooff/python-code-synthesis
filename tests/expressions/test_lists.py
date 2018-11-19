from ast import *
from unittest import TestCase
from evalo.evalo import eval_expro
from kanren import var, run


class TestLists(TestCase):
    def setUp(self):
        pass

    def run_expr(self, expr, value, eval_expr=False, env=list(), maxdepth=3):
        goals = eval_expro(expr, env, value, maxdepth=maxdepth)
        results = run(5, expr if eval_expr else value, goals)
        print('Evaluated results: {}'.
              format([dump(x) if isinstance(x, AST) else x for x in results]))
        return results

    def test_empty_list_ast_evaluates_to_empty_list(self):
        ast_expr = List(elts=[])
        ret = self.run_expr(ast_expr, var())
        self.assertEqual(ret[0], [])

    def test_list_with_one_element_evaluates_to_list_with_one_element(self):
        ast_expr = List(elts=[Num(n=1)])
        ret = self.run_expr(ast_expr, var())
        self.assertEqual(ret[0], [1])

    def test_list_with_ints_evaluates_to_list_with_ints(self):
        ast_expr = List(elts=[Num(n=1), Num(n=2)])
        ret = self.run_expr(ast_expr, var())
        self.assertEqual(ret[0], [1, 2])

    # Reenable this after the performance is improved, as this test
    # takes about a minute
    #def test_nested_list_evaluates_every_list(self):
    #    ast_expr = List(elts=[List(elts=[Num(n=1)]), Num(n=2)])
    #    ret = self.run_expr(ast_expr, var(), maxdepth=5)
    #    self.assertEqual(ret[0], [[1], 2])
