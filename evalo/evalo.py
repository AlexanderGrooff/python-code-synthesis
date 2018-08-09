from uuid import uuid4
from kanren import eq, vars, conde, goalify, isvar, var, run, unifiable, lany, \
    lall, membero
from kanren.arith import add
from kanren.core import EarlyGoalError, success, fail
from unification.more import unify_object
import ast

typeo = goalify(type)


goal_stack = {}


def args_to_hash(f, args):
    return str(hash(str(f) + str(args)))


def eval_to_stack(f, args):
    if not args:
        return True
    h = args_to_hash(f, args)
    current_stack = goal_stack.get(h, [])
    # If a call is already on the stack, that means there is a duplicate
    if current_stack:
        print('Found double call to {} with args {}'.format(str(f), args))
        goal_stack[h] = []
        return False
    else:
        goal_stack[h] = args
        return True


def evalo(program, value):
    unifiable(ast.AST)
    return eval_programo(program, [], value)


def eval_programo(program, env, value, previous_args=None):
    print('Evaluating program {} to {} with env {}'.format(program, value, env))
    current_args = (program, env, value)
    if not eval_to_stack(eval_programo, current_args):
        return fail

    return conde(
        ((eval_stmto, program, env, value, previous_args),),  # Change this
    )


def eval_stmto(stmt, env, value, previous_args=None):
    print('Evaluating stmt {} to {} with env {}'.format(stmt, value, env))
    #current_args = (stmt, env, value)
    #if not eval_to_stack(eval_stmto, current_args):
    #    return fail

    exprbody = var('exprbody')
    return conde(
        ((eq, stmt, ast.Expr(value=exprbody)),  # Expressions
         (eval_expro, exprbody, env, value)),
    )


def eval_expro(expr, env, value, previous_args=None):
    print('Evaluating expr {} to {} with env {}'.format(expr, value, env))

    op = var('op')
    v1 = var('v1')
    v2 = var('v2')
    e1 = var('e1')
    e2 = var('e2')
    if isinstance(expr, ast.AST):
        print('Found AST for expr -> {}'.format(ast.dump(expr)))
    if isinstance(value, ast.AST):
        print('Found AST for value -> {}'.format(ast.dump(value)))
    return conde(
        ((eq, expr, ast.Num(n=value)),
         (membero, value, [0,1,2])),
        ((eq, expr, ast.BinOp(left=e1, op=op, right=e2)),  # Expressions
         (eq, op, ast.Add()),
         (eval_expro, e1, env, v1, None),
         (eval_expro, e2, env, v2, None),
         (add, v1, v2, value)),
    )
