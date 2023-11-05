import datetime
import re

from tarotools.taro.jobs.instance import InstancePhase


class AllFilter:

    def __init__(self):
        self.filters = []

    def __ilshift__(self, j_filter):
        self.filters.append(j_filter)
        return self

    def __call__(self, job_info):
        return all(f(job_info) for f in self.filters)


def create_id_filter(text):
    pattern = re.compile(text)

    def do_filter(job_info):
        return pattern.search(job_info.job_id) or pattern.search(job_info.run_id)

    return do_filter


def finished_filter(job_info):
    return job_info.phase.in_phase(InstancePhase.TERMINAL)


def today_filter(job_info):
    return job_info.lifecycle.started_at(InstancePhase.CREATED).astimezone().date() == \
           datetime.datetime.today().date()


def yesterday_filter(job_info):
    return job_info.lifecycle.started_at(InstancePhase.CREATED).astimezone().date() == \
           (datetime.datetime.today().date() - datetime.timedelta(days=1))


def create_since_filter(since):
    def do_filter(job_info):
        return job_info.lifecycle.started_at(InstancePhase.CREATED).astimezone().replace(tzinfo=None) >= since

    return do_filter


def create_until_filter(until):
    return lambda j: not create_since_filter(until)(j)
