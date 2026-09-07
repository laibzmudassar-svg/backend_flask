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


def notify_post_author(post_id, comment_id):
    """Background job: notify the post author that a new comment was added.
    Runs via the RQ worker — does not block the comment creation request."""
    from app import app
    from extensions import db
    from models.post_model import Post
    from models.comment_model import Comment

    with app.app_context():
        post = Post.query.get(post_id)
        comment = Comment.query.get(comment_id)

        if not post or not comment:
            print(f"[notify_post_author] Post or comment not found (post_id={post_id}, comment_id={comment_id})")
            return

        print(f"[notify_post_author] Notifying author of post '{post.title}' — new comment: \"{comment.text}\"")
        # In a real system, this would send an email/push notification.
        # Kept simple here to focus on demonstrating the async queuing pattern.