import ast
from functools import partial
from typing import Callable, Union

from kanren.core import goaleval, lall
from kanren.util import take, unique, multihash
from unification import Var, reify, var

from evalo.evalo import eval_expro


class LambdaCompletionFramework:
    n = None
    goals = []

    def __init__(self, target: Callable, target_var: Var, n: Union[int, None] = None):
        self.target = target
        self.target_var = target_var
        self.n = n
        self.lambda_var = var(self.target.__name__)

    def add_goal(self, input_args=None, output=None):
        if input_args is None:
            input_args = []
        call = ast.Call(func=self.lambda_var, args=input_args, keywords=[])
        goals = eval_expro(expr=call, value=output, env=[[self.lambda_var, self.target]])
        self.goals.append(goals)
        return goals

    def fill_in_lambda(self):
        tuple_goals = tuple(self.goals)
        reify_target_lambda = partial(reify, self.target_var)
        goal_evaluator = goaleval(lall(tuple_goals))
        if isinstance(goal_evaluator, Callable):
            goal_evaluator = goal_evaluator({})
        results = map(reify_target_lambda, goal_evaluator)
        return take(self.n, unique(results, key=multihash))
