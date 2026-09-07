import json
from extensions import redis_client

pubsub = redis_client.pubsub()
pubsub.subscribe("domain_events")

print("Listening for domain events...")
for message in pubsub.listen():
    if message["type"] == "message":
        event = json.loads(message["data"])
        print(f"Received event: {event['event']} | data: {event['data']}")