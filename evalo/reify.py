from collections.abc import Mapping
from types import FunctionType
from typing import Optional, List

from codetransformer import CodeTransformer, instructions, pattern, Code
from codetransformer.instructions import Instruction
from loguru import logger
from unification import var
from unification.core import construction_sentinel, _reify, reify

from evalo.utils import explode_function


def init_reify():
    _reify.add((FunctionType, Mapping), _reify_FunctionType)


def val_to_instrs(v) -> Optional[List[Instruction]]:
    # TODO: Definitely not fool-proof to get a code object
    try:
        code = compile(str(v), "", "eval")
    except Exception as e:
        logger.warning(f"Couldn't compile {v} to instructions, got error: {e}")
        return
    instrs = Code.from_pycode(code).instrs
    # Compile always appends a return, so remove that
    if instrs[-1].equiv(instructions.RETURN_VALUE()):
        instrs = instrs[: len(instrs) - 1]
    return instrs


def replace_logicvar_with_val(f, logicvar_name, val):
    class ReplaceLogicVar(CodeTransformer):
        @pattern(instructions.LOAD_GLOBAL | instructions.LOAD_DEREF)
        def _replace_logicvar(self, loadlogicvar):
            new_instrs = val_to_instrs(val)
            if not new_instrs:
                yield loadlogicvar
                return
            if loadlogicvar.arg == logicvar_name:
                logger.info("Replacing {} with {}".format(loadlogicvar, val))
                for instr in new_instrs:
                    yield instr.steal(loadlogicvar)
                # yield instructions.LOAD_CONST(val).steal(loadlogicvar)
            else:
                logger.info(
                    f"Couldn't find {logicvar_name} in instruction {loadlogicvar}"
                )
                yield loadlogicvar

    transformer = ReplaceLogicVar()
    return transformer(f)


def name_from_global(f: FunctionType, s: Mapping, name: str) -> Optional[object]:
    """
    Transform an unknown name in the function to a value
    """
    try:
        logicvar = f.__globals__[name]
        # if not isvar(logicvar):
        #     logger.info("Tried reifying {} but {} is not a LV".format(name, logicvar))
        #     return
        reified_v = reify(logicvar, s)
        logger.info("Reified {} to {}".format(logicvar, reified_v))
        return reified_v
    except (IndexError, KeyError):
        pass


def name_as_lv(s: Mapping, name: str) -> Optional[object]:
    lv = var(name)
    v = s.get(lv)
    if v != lv:
        logger.info("Found {} to be a logicvar with value {}".format(name, v))
        return v
    logger.info(f"{name} is not a mapped logicvar")


def _reify_FunctionType(f: FunctionType, s: Mapping):
    logger.info(f"Reifying function {f}")
    shadow_dict = {}
    c = f.__code__
    reifiable_names = c.co_names + c.co_freevars
    for global_name in reifiable_names:
        v = name_from_global(f, s, name=global_name)
        if v is not None:
            shadow_dict[global_name] = v
            continue
        v = name_as_lv(s, name=global_name)
        if v is not None:
            shadow_dict[global_name] = v

    logger.info(
        "Reified all vars {} in function. Found shadowdict {}".format(
            reifiable_names, shadow_dict
        )
    )
    if shadow_dict:
        for logicvar, val in shadow_dict.items():
            logger.info(f"Starting replacement of {logicvar} with {val}")
            f = replace_logicvar_with_val(f, logicvar, val)
        new_c = Code.from_pyfunc(f)
        logger.info(f"New instructions: {new_c.instrs}")

        yield construction_sentinel
        yield f
    else:
        yield f
