import logging

import pyposto.core as ppc

logging.basicConfig()

logger: logging.Logger = logging.getLogger(__name__)


def do(step, log=None):
    if log:
        logger.info(log)

    def wrapper(target: ppc.CommandInvoker):
        if isinstance(target, ppc.CommandInvoker):
            target.add_step(step)
            return target
        else:
            return ppc.CommandInvoker(target, step)

    return wrapper
