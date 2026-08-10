import time
import random


def send_welcome_email(name, email):
    """Simulates a heavy task (e.g., sending an email) that takes time."""
    print(f"[WORKER] Starting welcome email task for {email}...")

    # Simulate a slow operation (e.g., real SMTP call would take time)
    time.sleep(3)

    print(f"[WORKER] Welcome email sent successfully to {name} <{email}>")

    return {"status": "sent", "email": email}


def send_report_email(name, email):
    """Simulates an unreliable task that sometimes fails (e.g., transient network timeout)."""
    print(f"[WORKER] Attempting to send report email to {email}...")

    # Simulate a transient failure ~70% of the time, to demonstrate retries
    if random.random() < 0.7:
        raise ConnectionError(f"Simulated network timeout while emailing {email}")

    print(f"[WORKER] Report email sent successfully to {name} <{email}>")
    return {"status": "sent", "email": email}