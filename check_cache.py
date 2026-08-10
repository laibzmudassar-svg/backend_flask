from extensions import redis_client

value = redis_client.get("users")

print("Cached Users:")
print(value)