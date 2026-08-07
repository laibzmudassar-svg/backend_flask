import jwt
import os
from functools import wraps
from flask import request, jsonify, g


def authenticate_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        # --- Extract & Validate Token ---
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "Missing or malformed token"
            }), 401

        token = auth_header.split(" ")[1]

        # --- Verify JWT Signature ---
        try:
            jwt_secret = os.getenv("JWT_SECRET")
            decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token has expired"
            }), 403
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": "Invalid token"
            }), 403

        # --- Attach Context ---
        g.user = decoded

        return f(*args, **kwargs)

    return decorated