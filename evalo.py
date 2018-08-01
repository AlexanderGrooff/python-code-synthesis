from kanren import run, eq, var, vars, conde, goalify, lany
import ast

typeo = goalify(type)

def evalo(expr, value):
    return eval_expro(expr, [], value)


def eval_expro(expr, env, value):
    x, y = vars(2)
    return conde(
        (eq(expr, ast.Num(n=x)),  # Numbers
         lany(typeo(x, int), 
              typeo(x, float))),
        (eq(expr,value),),  # Not implemented yet
    )
