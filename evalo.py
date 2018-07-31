from kanren import run, eq, var, conde

def evalo(expr, value):
    return eval_expro(expr, [], value)


def eval_expro(expr, env, value):
    return conde([
        eq(expr, value)
    ])

x = var()
print(run(1, x, evalo('1', x)))
