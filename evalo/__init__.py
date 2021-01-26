import ast
import astunparse

from evalo.evalo import evalo, eval_expro, eval_stmto, init_evalo
from evalo.utils import ast_dump_if_possible, sort_by_complexity
from kanren import run, var

init_evalo()
