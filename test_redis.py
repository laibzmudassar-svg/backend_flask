from extensions import redis_client

# Set a test key with 60 seconds TTL
redis_client.set("test_key", "hello from flask", ex=60)

# Get it back
value = redis_client.get("test_key")
print("Value from Redis:", value)

# Check TTL (time remaining)
ttl = redis_client.ttl("test_key")
print("TTL remaining (seconds):", ttl)

# Delete the key
redis_client.delete("test_key")
print("Key deleted successfully.")

# Verify deletion
value = redis_client.get("test_key")
print("Value after deletion:", value)