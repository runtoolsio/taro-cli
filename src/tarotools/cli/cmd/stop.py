from tarotools.cli import printer, style, argsutil, cliutil
from tarotools.cli.printer import print_styled
from tarotools.cli.view.instance import JOB_ID, INSTANCE_ID, CREATED, STATE
from tarotools.taro.client import APIClient
from tarotools.taro.util import MatchingStrategy


def run(args):
    with APIClient() as client:
        instance_match = argsutil.instance_matching_criteria(args, MatchingStrategy.FN_MATCH)
        stop_jobs, _ = client.read_job_instances(instance_match)

        if not stop_jobs:
            print('No instances to stop: ' + " ".join(args.instances))
            return

        if not args.force:
            print('Instances to stop:')
            printer.print_table(stop_jobs, [JOB_ID, INSTANCE_ID, CREATED, STATE], show_header=True, pager=False)
            if not cliutil.user_confirmation(yes_on_empty=True, catch_interrupt=True):
                return

        for stop_resp in client.stop_instances(instance_match).responses:
            print_styled(*style.job_instance_id_styled(stop_resp.instance_metadata.id) + [('', ' -> '), ('', stop_resp.stop_result)])