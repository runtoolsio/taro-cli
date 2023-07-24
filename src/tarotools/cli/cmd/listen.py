import sys

from tarotools.taro.listening import StateReceiver, ExecutionStateEventObserver
from tarotools.taro.util import MatchingStrategy, DateTimeFormat
from tarotools.cli import argsutil
from tarotools.cli import printer, style, cliutil


def run(args):
    receiver = StateReceiver(argsutil.id_match(args, MatchingStrategy.PARTIAL))
    receiver.listeners.append(EventPrint(receiver, args.timestamp.value))
    receiver.start()
    cliutil.exit_on_signal(cleanups=[receiver.close_and_wait])
    receiver.wait()  # Prevents 'exception ignored in: <module 'threading' from ...>` error message


class EventPrint(ExecutionStateEventObserver):

    def __init__(self, receiver, ts_format=DateTimeFormat.DATE_TIME_MS_LOCAL_ZONE):
        self._receiver = receiver
        self.ts_format = ts_format

    def state_update(self, instance_meta, previous_state, new_state, changed):
        try:
            printer.print_styled(*style.job_instance_id_status_line_styled(
                instance_meta.id, new_state, changed, ts_prefix_format=self.ts_format))
            sys.stdout.flush()
        except BrokenPipeError:
            self._receiver.close_and_wait()
            cliutil.handle_broken_pipe(exit_code=1)