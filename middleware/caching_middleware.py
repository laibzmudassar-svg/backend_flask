import json
import zlib
from functools import wraps
from flask import request, jsonify
from extensions import redis_client


def cache_response(prefix, ttl=60):
    """
    Reusable caching decorator for GET routes.
    Compresses JSON data with zlib before storing in Redis to save memory.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{request.path}:{request.query_string.decode()}"

            cached_data = redis_client.get(cache_key)
            if cached_data:
                print(f"CACHE HIT: {cache_key}")
                # Decompress before decoding JSON
                decompressed = zlib.decompress(cached_data.encode("latin1"))
                return jsonify(json.loads(decompressed)), 200

            print(f"CACHE MISS: {cache_key}")
            response, status_code = func(*args, **kwargs)

            # Serialize to JSON, then compress before storing
            json_data = json.dumps(response.get_json())
            compressed = zlib.compress(json_data.encode("utf-8"))
            redis_client.setex(cache_key, ttl, compressed.decode("latin1"))

            return response, status_code
        return wrapper
    return decorator