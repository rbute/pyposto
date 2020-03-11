import logging

import pyposto.core as ppc

logging.basicConfig()

logger: logging.Logger = logging.getLogger(__name__)


def config(configuration):
    conf: dict = None

    if isinstance(configuration, dict):
        conf = configuration
    else:
        conf = {}

    def config_wrapper(fun):

        if isinstance(fun, ppc.CommandInvoker):
            fun.update_config(conf)
            return fun
        else:
            raise Exception('Attempt to invoke @config more than once')

    return config_wrapper


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
