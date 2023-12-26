"""Define a simple memoization decorator."""

import json
import logging
from collections import defaultdict
from typing import Any, Callable, Dict

from utils import logger


MEMORY: Dict[str, Dict[int, Any]] = defaultdict(dict)


def get_name(func: Callable) -> str:
    return f"{func.__qualname__}: 0x{id(func):x}"


def get_arg_hash(*args, **kwargs) -> int:
    sorted_kwargs = dict(sorted(kwargs.items()))
    all_args = (args, sorted_kwargs)
    all_args_str = json.dumps(all_args)
    return hash(all_args_str)


def memo(func: Callable) -> Callable:
    func_name = get_name(func)

    def wrapper(*args, **kwargs):
        log = logger.isEnabledFor(logging.DEBUG)

        if log:
            s = func.__qualname__ + "("
            s += ", ".join(str(_) for _ in args)
            s += ", ".join(f"{key}={value}" for key, value in kwargs.items())
            s += ")"

        arg_hash = get_arg_hash(*args, **kwargs)
        if func_name in MEMORY:
            all_results = MEMORY[func_name]

            value = all_results.get(arg_hash)
            if value is not None:
                if log:
                    logger.debug(f"{s} found in memory, retrieving.")
                return value
            else:
                if log:
                    logger.debug(f"{s} not found in memory, calculating.")
        else:
            if log:
                logger.debug(f"{func.__qualname__} is a new function, calculating.")

        value = func(*args, **kwargs)
        MEMORY[func_name][arg_hash] = value
        if log:
            logger.debug(f"{s} stored in memory.")

        return value

    return wrapper
