from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError


def validate_body(schema_class):
    """
    Decorator that validates incoming JSON request body
    against the given Pydantic schema class.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json_data = request.get_json(silent=True)

            if json_data is None:
                return jsonify({"error": "Request body must be valid JSON"}), 400

            try:
                validated_data = schema_class(**json_data)
            except ValidationError as e:
                errors = [
                    {"field": err["loc"][0], "message": err["msg"]}
                    for err in e.errors()
                ]
                return jsonify({"error": "Validation failed", "details": errors}), 400

            # Pass validated data into the route function
            kwargs["validated_data"] = validated_data
            return func(*args, **kwargs)
        return wrapper
    return decorator