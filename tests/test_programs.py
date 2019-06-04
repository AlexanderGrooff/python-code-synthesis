import ast
from unittest import TestCase
from kanren import var, run

from evalo.evalo import eval_programo


class TestPrograms(TestCase):
    def run_program(self, program, value, eval_program=False, env=list()):
        results = run(5, program if eval_program else value, eval_programo(program, env, value))
        print('Evaluated results: {}'.format([ast.dump(x) if isinstance(x, ast.AST) else x for x in results]))
        return results

    def test_program_is_evaluated_to_value(self):
        ret = self.run_program(ast.Expr(value=ast.Num(n=1)), var('expected_var'))
        self.assertEqual(ret[0], 1)
