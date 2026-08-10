from rq import SimpleWorker
from extensions import rq_redis_conn

if __name__ == "__main__":
    worker = SimpleWorker(["default"], connection=rq_redis_conn)
    print("[WORKER] Listening for jobs on 'default' queue (with scheduler)...")
    worker.work(with_scheduler=True)
    
    