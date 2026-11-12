"""In-process asynchronous job queue for slow work (QAOA runs, large fleets).

Submissions return immediately with a job id; one worker drains the queue and shares the
API's optimization slot, so synchronous and queued work never run QAOA concurrently.
A production deployment would swap this for Redis/RQ or Celery with the same contract.
"""
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)
MAX_RETAINED = 200


def now():
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self, slot, workers=1):
        self.slot = slot
        self.workers = workers
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="anavo-job")
        self.jobs = OrderedDict()
        self.lock = Lock()

    def submit(self, kind, function, request):
        job_id = uuid4().hex
        with self.lock:
            self.jobs[job_id] = dict(job_id=job_id, kind=kind, status="queued", submitted_utc=now())
            self._evict()
        self.pool.submit(self._run, job_id, function, request)
        return self.get(job_id)

    def _run(self, job_id, function, request):
        with self.slot:  # blocking: queued jobs wait for the shared optimization slot
            self._update(job_id, status="running", started_utc=now())
            try:
                result = function(request)
                self._update(job_id, status="succeeded", finished_utc=now(),
                             result=result.model_dump(mode="json"))
            except Exception as exc:  # report, never fabricate a result
                logger.exception("Job %s failed", job_id)
                self._update(job_id, status="failed", finished_utc=now(),
                             error=str(exc) if isinstance(exc, ValueError) else "Job failed; consult backend logs.")

    def _update(self, job_id, **fields):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(fields)

    def _evict(self):
        finished = [k for k, v in self.jobs.items() if v["status"] in ("succeeded", "failed")]
        while len(self.jobs) > MAX_RETAINED and finished:
            self.jobs.pop(finished.pop(0))

    def get(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            if job is None:
                return None
            job = dict(job)
            if job["status"] == "queued":
                queued = [k for k, v in self.jobs.items() if v["status"] == "queued"]
                job["queue_position"] = queued.index(job_id) + 1
            return job

    def summary(self):
        with self.lock:
            items = [dict(v, result=None) for v in reversed(self.jobs.values())][:50]
            states = [v["status"] for v in self.jobs.values()]
        return dict(jobs=items, workers=self.workers, queued=states.count("queued"),
                    running=states.count("running"))
