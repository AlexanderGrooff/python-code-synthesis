from types import FunctionType
from uuid import uuid4

from kanren import eq, lall
from kanren.constraints import ConstrainedState, isinstanceo
from kanren.term import applyo
from unification import reify, var
from unification.core import isground


def typeo(v, t):
    def typeo_goal(S: ConstrainedState):
        nonlocal v, t

        v_rf, t_rf = reify((v, t), S)
        isground_all = [isground(reified_value, S) for reified_value in [v_rf, t_rf]]
        if not all(isground_all):
            if not isground(t_rf, S):
                g = eq(type(v_rf), t_rf)
                yield from g(S)
            else:
                # This doesn't put a value to v_rf, but constrains it to the given type
                g = isinstanceo(v_rf, t_rf)
                yield from g(S)
        else:
            if type(v_rf) == t_rf:
                yield S

    return typeo_goal


def binopo(x, y, v, op):
    def binopo_goal(S: ConstrainedState):
        nonlocal x, y, v, op

        uuid = str(uuid4())[:4]
        t = var("type_" + uuid)
        x_rf, y_rf, v_rf, op_rf = reify((x, y, v, op), S)
        isground_all = [
            isground(reified_value, S) for reified_value in [x_rf, y_rf, v_rf, op_rf]
        ]
        if not all(isground_all):
            # We can only fix one LV at a time
            if len([uv for uv in isground_all if uv is False]) == 1:
                # TODO: Revop the other vars
                if not isground(v_rf, S):
                    try:
                        g = lall(
                            isinstanceo(x_rf, t),
                            isinstanceo(y_rf, t),
                            isinstanceo(v_rf, t),
                            eq(op_rf(x_rf, y_rf), v_rf),
                        )
                    except Exception:
                        return
                    yield from g(S)
        else:
            # TODO: Why isnt this covered by the `typeo` goal?
            try:
                g = lall(
                    isinstanceo(x_rf, t),
                    isinstanceo(y_rf, t),
                    isinstanceo(v_rf, t),
                    eq(op_rf(x_rf, y_rf), v_rf),
                )
            except Exception as e:
                return
            yield from g(S)

    return binopo_goal


def callo(func, args, val):
    def callo_goal(S: ConstrainedState):
        nonlocal func, args, val

        func_rf, args_rf, val_rf = reify((func, args, val), S)
        isground_all = [
            isground(reified_value, S) for reified_value in [func_rf, args_rf, val_rf]
        ]
        if not all(isground_all):
            if len([v for v in isground_all if v is False]) == 1:
                if isground(func_rf, S):
                    if isinstance(func_rf, FunctionType):
                        g = eq(func_rf(*args), val_rf)
                        yield from g(S)
                elif isground(val_rf, S):
                    g = lall(
                        applyo(func_rf, args, val),
                        typeo(func_rf, FunctionType),
                    )
                    yield from g(S)
                else:
                    raise NotImplementedError("Can't handle args yet")
        else:
            if isinstance(func_rf, FunctionType) and func_rf(*args) == val:
                yield S

    return callo_goal
