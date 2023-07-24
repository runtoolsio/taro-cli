import sys

import tarotools.taro.client
from tarotools.taro.jobs.inst import InstanceMatchingCriteria, compound_id_filter
from tarotools.taro.listening import OutputReceiver, OutputEventObserver
from tarotools.taro.theme import Theme
from tarotools.taro.util import MatchingStrategy
from tarotools.cli import argsutil
from tarotools.cli import printer, style, cliutil

HIGHLIGHT_TOKEN = (Theme.separator, ' ---> ')


def run(args):
    id_criteria = argsutil.id_matching_criteria(args, MatchingStrategy.PARTIAL)
    if args.follow:
        receiver = OutputReceiver(compound_id_filter(id_criteria))
        receiver.listeners.append(TailPrint(receiver))
        receiver.start()
        cliutil.exit_on_signal(cleanups=[receiver.close_and_wait])
        receiver.wait()  # Prevents 'exception ignored in: <module 'threading' from ...>` error message
    else:
        for tail_resp in taro.client.read_tail(InstanceMatchingCriteria(id_criteria)).responses:
            printer.print_styled(HIGHLIGHT_TOKEN, *style.job_instance_id_styled(tail_resp.instance_metadata.id))
            for line, is_error in tail_resp.tail:
                print(line, file=sys.stderr if is_error else sys.stdout)
            sys.stdout.flush()


class TailPrint(OutputEventObserver):

    def __init__(self, receiver):
        self._receiver = receiver
        self.last_printed_job_instance = None

    def output_event_update(self, instance_meta, output, is_error):
        # TODO It seems that this needs locking
        try:
            if self.last_printed_job_instance != instance_meta.id:
                printer.print_styled(HIGHLIGHT_TOKEN, *style.job_instance_id_styled(instance_meta.id))
            self.last_printed_job_instance = instance_meta.id
            print(output, flush=True, file=sys.stderr if is_error else sys.stdout)
        except BrokenPipeError:
            self._receiver.close_and_wait()
            cliutil.handle_broken_pipe(exit_code=1)