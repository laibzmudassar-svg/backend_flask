import bcrypt
import jwt
import os
import datetime
import json
from extensions import redis_client, task_queue
from flask import request, jsonify, g, abort
from models.user_model import User
from extensions import db
from middleware.validation_middleware import validate_body
from schemas.user_schema import UserRegisterSchema, UserLoginSchema
from tasks import send_welcome_email
from rq import Retry
from tasks import send_welcome_email, send_report_email

def create_user():
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        abort(400, description="Missing name or email")

    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()

    # Remove old cache because data has changed
    redis_client.delete("users")

    return jsonify({
        "message": "User created successfully",
        "name": user.name,
        "email": user.email
    }), 201

def get_users():
    
    # Check Redis cache first
    cached_users = redis_client.get("users")

    if cached_users:
        print("Data coming from Redis Cache")
        return jsonify(json.loads(cached_users)), 200

    # Get users from database
    users = User.query.all()

    users_data = [user.to_dict() for user in users]

    # Store users in Redis cache for 60 seconds
    redis_client.setex(
        "users",
        60,
        json.dumps(users_data)
    )

    print("Data coming from Database")

    return jsonify(users_data), 200


def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        abort(404, description="User not found")

    return jsonify(user.to_dict()), 200


@validate_body(UserRegisterSchema)
def register_user(validated_data=None):
    name = validated_data.name
    email = validated_data.email
    password = validated_data.password

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        abort(400, description="Email already registered")

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )

    user = User(
        name=name,
        email=email,
        password_hash=password_hash.decode("utf-8")
    )

    db.session.add(user)
    db.session.commit()

    # --- Enqueue Producer: publish welcome-email job to the queue ---
    # This runs in the background via the worker, so this route
    # does NOT wait for the "email" to be sent — it returns immediately.
    task_queue.enqueue(send_welcome_email, user.name, user.email)

    return jsonify({
        "message": "User registered successfully",
        "name": user.name,
        "email": user.email
    }), 201


@validate_body(UserLoginSchema)
def login_user(validated_data=None):

    email = validated_data.email
    password = validated_data.password

    user = User.query.filter_by(email=email).first()

    if not user or not user.password_hash:
        abort(401, description="Invalid email or password")

    stored_hash = user.password_hash.encode("utf-8")

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    )

    if not password_correct:
        abort(401, description="Invalid email or password")

    token_payload = {
        "userId": user.id,
        "email": user.email,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1)
    }

    jwt_secret = os.getenv("JWT_SECRET")

    token = jwt.encode(
        token_payload,
        jwt_secret,
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "name": user.name,
        "email": user.email,
        "token": token
    }), 200


def get_profile():

    user_id = g.user["userId"]

    user = User.query.get(user_id)

    if not user:
        abort(404, description="User not found")

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    }), 200
    
def send_report():
    """Test endpoint: enqueues an unreliable task with exponential backoff retries."""
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        abort(400, description="Missing name or email")

    job = task_queue.enqueue(
        send_report_email,
        data["name"],
        data["email"],
        retry=Retry(max=3, interval=[10, 30, 60])
    )

    return jsonify({
        "message": "Report email task queued",
        "job_id": job.id
    }), 202
    