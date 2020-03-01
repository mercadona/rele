import signal
import sys

import rele
from rele import Worker


def create_worker(subs, config):
    for sub in subs:
        sys.stdout.write(f"  {sub}")
    worker = Worker(
        subs,
        config.gc_project_id,
        config.credentials,
        config.ack_deadline,
        config.threads_per_subscription,
    )

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(signal.SIGTSTP, worker.stop)

    worker.run_forever()


def _autodiscover_subs(sub_modules, settings, config):
    return rele.config.load_subscriptions_from_paths(
        sub_modules,
        config.sub_prefix,
        settings.RELE.get("FILTER_SUBS_BY"),
    )
