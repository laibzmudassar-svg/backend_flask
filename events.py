import json
from extensions import redis_client

def publish_event(event_name, data):
    """Publishes a domain event to a Redis Pub/Sub channel."""
    payload = json.dumps({"event": event_name, "data": data})
    redis_client.publish("domain_events", payload)
    print(f"Published event: {event_name} -> {data}")