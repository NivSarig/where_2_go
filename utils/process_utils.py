from functools import partial

from builtins import object
from future import standard_library
import subprocess
from threading import Thread

import os
import logging
from time import time

standard_library.install_aliases()

if os.name != "nt":
    # This doesn't work on windows - As it the path that uses should never be called on windows it doesn't matter.
    # (The file is imported)
    import psutil

logger = logging.getLogger(__name__)


def call_process_and_log_output(process_string, logger=None):
    """
    Invoke A process that will run process_string
    :param process_string: The process string to run
    :type process_string: str
    :param logger: logger
    :type logger: logging.Logger
    :param elapsed_callback: Elapsed callback
    :type elapsed_callback: Any
    :return: Return code
    :rtype: int
    """
    if logger:
        logger.info(u"Running process_string: {}".format(process_string))
    abortable_process = AbortableSubprocess(process_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    return abortable_process.run()


class AbortableSubprocess(object):
    """
    Runs a sub process, killing it if current context is aborted
    """

    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.process = None

    def run(self):
        def target():
            self.process = subprocess.Popen(self.args, **self.kwargs)
            self.process.communicate()

        start = time()
        thread = Thread(target=target, name="Abortable-Process-Tracker")
        thread.setDaemon(True)
        thread.start()

        while thread.is_alive():
            thread.join(1)
            logger.info(u"Abortion detection, killing subprocess...")
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except psutil.NoSuchProcess as e:
                logger.warning(
                    u"Could not find parent {} and kill its children. Error: {}".format(self.process.pid, e)
                )
            thread.join()
        return self.process.returncode
