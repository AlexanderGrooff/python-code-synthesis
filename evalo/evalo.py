from types import FunctionType
from uuid import uuid4
from kanren import eq, vars, conde, goalify, isvar, var, run, unifiable, lany, \
    lall, membero
from kanren.arith import add, sub, mul, div, mod
from kanren.core import EarlyGoalError, success, fail
from kanren.goals import heado, tailo, appendo
from unification.more import unify_object
import ast

typeo = goalify(type)
goal_stack = {}

unifiable(ast.AST)


def callo(func, val):
    if not isvar(func):
        return (eq, func(), val)
    raise EarlyGoalError()


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


def eval_expro(expr, env, value):
    print('Evaluating expr {} to {} with env {}'.format(expr, value, env))

    uuid = str(uuid4())[:4]

    op = var('op' + uuid)
    op_v = var('op_v' + uuid)
    v1 = var('v1' + uuid)
    v2 = var('v2' + uuid)
    e1 = var('e1' + uuid)
    e2 = var('e2' + uuid)
    name = var('name' + uuid)
    body = var('body' + uuid)
    body_v = var('body_v' + uuid)
    args = var('args' + uuid)
    args_v = var('args_v' + uuid)
    func = var('func' + uuid)
    func_v = var('func_v' + uuid)
    kwargs = var('kwargs' + uuid)
    kwargs_v = var('kwargs_v' + uuid)
    str_e = var('str_e' + uuid)
    if isinstance(expr, ast.AST):
        print('Found AST for expr -> {}'.format(ast.dump(expr)))
    if isinstance(value, ast.AST):
        print('Found AST for value -> {}'.format(ast.dump(value)))
    return (conde,
        ((eq, expr, ast.Name(id=name, ctx=ast.Load())),
         (lookupo, name, env, value)),
        ((eq, expr, ast.Str(s=str_e)),
         (typeo, value, str),
         (eq, str_e, value)),
        ((eq, expr, ast.Num(n=value)),
         (membero, value, range(100))),
        ((eq, expr, ast.BinOp(left=e1, op=op, right=e2)),
         (eval_opo, op, env, op_v),
         (eval_expro, e1, env, v1),
         (eval_expro, e2, env, v2),
         (op_v, v1, v2, value)),
        ((eq, expr, ast.Lambda(body=body, args=[])),
         (typeo, value, FunctionType),
         (eval_expro, body, env, body_v),
         (eq, lambda: body_v, value)),
        ((eq, expr, ast.Call(func=func, args=[], keywords=[])),
         (eval_expro, func, env, func_v),
         (callo, func_v, value))
    )


def lookupo(name, env, t):
    head = var()
    rest = var()
    key = var()
    val = var()
    return (conde,
        ((heado, head, env),
         (heado, name, head),
         (tailo, rest, head),
         (heado, t, rest)),
        ((tailo, rest, env),
         (lookupo, name, rest, t))
    )


def eval_opo(op, env, value):
    print('Evaluating operator {} to {} with env {}'.format(op, value, env))

    return (conde,
        ((eq, op, ast.Add()),
         (eq, value, add)),
        ((eq, op, ast.Sub()),
         (eq, value, sub)),
        ((eq, op, ast.Mult()),
         (eq, value, mul)),
        #((eq, op, ast.Div()),  # Float is not yet supported
        # (eq, value, div)),
        ((eq, op, ast.Mod()),
         (eq, value, mod)),
    )
