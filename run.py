#!/usr/bin/env python
import ast
from argparse import ArgumentParser
from kanren import var, run

from evalo import evalo

parser = ArgumentParser(description='Evaluate a python file')
parser.add_argument('--path', help='Path to the file that should be interpreted')
parser.add_argument('--expr', '-e', help='Python expression that should be interpreted')
args = parser.parse_args()


def interp(expr):
    print("Program to be evaluated:\n{}".format(expr))
    program_ast = ast.parse(expr)
    program_ast = ast.Num(n=1)
    print("AST of the program: \n{}".format(ast.dump(program_ast)))
    x = var()
    evaluated_program = run(0, x, evalo(program_ast, x))
    print('Evaluated program: {}'.format(evaluated_program))


if args.path:
    with open(args.path, 'r') as fp:
        program = fp.read()
        if program[-1:] == '\n':
            program = program[:-1]
        interp(program)

if args.expr:
    interp(args.expr)
