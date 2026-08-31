import time
from rq.scheduler import RQScheduler
from extensions import rq_redis_conn

if __name__ == "__main__":
    scheduler = RQScheduler(queues=["default"], connection=rq_redis_conn)
    scheduler.acquire_locks()
    print("[SCHEDULER] Standalone RQ scheduler started, polling for due jobs...")
    while True:
        scheduler.enqueue_scheduled_jobs()
        time.sleep(5)