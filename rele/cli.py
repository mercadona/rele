import signal
import sys

import rele
from rele import Worker


def create_and_run_worker(subs, config):
    print(f"Configuring worker with {len(subs)} subscription(s)...")
    for sub in subs:
        print(f"  {sub}")
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


def autodiscover_subs(sub_modules, config):
    return rele.config.load_subscriptions_from_paths(
        sub_modules,
        config.sub_prefix,
        config.filter_by,
    )
