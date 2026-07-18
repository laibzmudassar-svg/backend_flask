from flask import request, jsonify
from models.user_model import get_user_by_id, add_user

def create_user():
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({
            "success": False,
            "error": "Missing name or email"
        }), 400

    name = data["name"]
    email = data["email"]
    new_id = len(data) + 100  # simple temporary id generator
    user = add_user(new_id, name, email)

    return jsonify({
        "message": "User created successfully",
        "name": user["name"],
        "email": user["email"]
    }), 201


def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404
    return jsonify(user), 200