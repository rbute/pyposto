import logging
import time

logging.basicConfig()

log: logging.Logger = logging.getLogger(__name__)


class CommandInvoker(object):

    def __init__(self, target, step):
        self.start_time = time.time()
        self.target = target
        self.steps: [] = [step]

    def add_step(self, step):
        self.steps.append(step)

    def __call__(self, *args, **kwargs):
        for step in self.steps:
            start_time = time.time()
            step(*args, **kwargs)
            end_time = time.time()
            log.info({
                'job_start': start_time,
                'job_end': end_time,
                'job_name': step.__name__,
                'job_duration': start_time - end_time,
            })
        self.target(*args, **kwargs)
        end_time = time.time()
        log.info({
            'job_start': self.start_time,
            'job_end': end_time,
            'job_name': self.target.__name__,
            'job_duration': self.start_time - end_time,
        })
