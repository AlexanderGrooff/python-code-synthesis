from collections.abc import Mapping
from inspect import signature
from types import FunctionType

from codetransformer import Code
from codetransformer.instructions import Instruction
from loguru import logger
from unification import var
from unification.core import _unify, assoc


def init_unify():
    _unify.add((FunctionType, FunctionType, Mapping), _unify_FunctionType)
    _unify.add((Instruction, Instruction, Mapping), _unify_Instruction)


def _unify_Instruction(i1, i2, s):
    logger.info("Unifying instruction {} to {}".format(i1, i2))
    if i1.equiv(i2):
        logger.info("Instructions {} and {} are equivalent".format(i1, i2))
        yield s
        return
    if i1.uses_name or i1.uses_free or i1.uses_varname:
        logger.info("Associating {} with {}".format(var(i1.arg), i2.arg))
        yield assoc(s, var(i1.arg), i2.arg)
        return
    if i2.uses_name or i2.uses_free or i2.uses_varname:
        logger.info("Associating {} with {}".format(var(i2.arg), i1.arg))
        yield assoc(s, var(i2.arg), i1.arg)
        return
    yield False


def _unify_FunctionType(f1: FunctionType, f2: FunctionType, s: Mapping):
    logger.info("Unifying {} to {}".format(f1, f2))
    if signature(f1) != signature(f2):
        logger.info("Signature doesn't match for function {} and {}".format(f1, f2))
        yield False
        return
    c_u = Code.from_pyfunc(f1)
    c_v = Code.from_pyfunc(f2)

    logger.info("Found instrs for u: {}".format(c_u.instrs))
    logger.info("Found instrs for v: {}".format(c_v.instrs))
    yield _unify(c_v.instrs, c_u.instrs, s)
