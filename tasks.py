import time
import random
from extensions import redis_client
from rq import get_current_job


def send_welcome_email(name, email):
    """Simulates a heavy task (e.g., sending an email) that takes time."""
    print(f"[WORKER] Starting welcome email task for {email}...")

    # Simulate a slow operation (e.g., real SMTP call would take time)
    time.sleep(3)

    print(f"[WORKER] Welcome email sent successfully to {name} <{email}>")

    return {"status": "sent", "email": email}


def send_report_email(name, email):
    """Simulates an unreliable task that sometimes fails (e.g., transient network timeout).
    Idempotent: uses a Redis flag keyed on the job ID so duplicate delivery of the
    same job (at-least-once semantics) does not resend an email that already succeeded.
    """
    job = get_current_job()
    idempotency_key = f"job_processed:{job.id}" if job else None

    # --- Idempotency check: skip if this exact job already completed successfully ---
    if idempotency_key and redis_client.get(idempotency_key):
        print(f"[WORKER] Job {job.id} already processed — skipping duplicate execution.")
        return {"status": "skipped_duplicate", "email": email}

    print(f"[WORKER] Attempting to send report email to {email}...")

    # Simulate a transient failure ~70% of the time, to demonstrate retries
    if random.random() < 0.7:
        raise ConnectionError(f"Simulated network timeout while emailing {email}")

    print(f"[WORKER] Report email sent successfully to {name} <{email}>")

    # Mark this job as successfully processed, so any duplicate delivery is skipped
    if idempotency_key:
        redis_client.setex(idempotency_key, 3600, "1")  # remember for 1 hour

    return {"status": "sent", "email": email}