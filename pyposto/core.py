import logging
import os
import time

logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'WARNING').upper()
)

log: logging.Logger = logging.getLogger(__name__)


class CommandInvoker(object):

    def __init__(self, target, steps, configuration: dict = {}):
        self.start_time = time.time()
        self.target = target
        self.steps: [] = [steps]
        self.config: dict = configuration

    def add_step(self, step):
        self.steps.append(step)

    def update_config(self, conf):
        self.config.update(conf)

    def __call__(self, *args, **kwargs):
        # config: dict = self.config
        self.steps.reverse()
        for step in self.steps:
            start_time = time.time()
            step(self.config)
            end_time = time.time()
            log.info({
                'job_start': start_time,
                'job_end': end_time,
                'job_name': step.__name__,
                'job_duration': end_time - start_time,
            })
            log.debug({
                'conf': self.config,
            })
        self.target(self.config)
        end_time = time.time()
        log.info({
            'job_start': self.start_time,
            'job_end': end_time,
            'job_name': self.target.__name__,
            'job_duration': end_time - self.start_time,
        })


