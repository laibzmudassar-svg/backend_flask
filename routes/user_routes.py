from flask import Blueprint
from controllers.user_controller import create_user, get_user, get_users, register_user, login_user, get_profile, send_report
from middleware.auth_middleware import authenticate_token
from extensions import limiter

user_bp = Blueprint("user_bp", __name__)

user_bp.route("/users", methods=["GET"])(get_users)
user_bp.route("/users", methods=["POST"])(authenticate_token(create_user))
user_bp.route("/users/<int:user_id>", methods=["GET"])(get_user)
user_bp.route("/auth/register", methods=["POST"])(register_user)
user_bp.route("/auth/login", methods=["POST"])(limiter.limit("10 per minute")(login_user))
user_bp.route("/auth/me", methods=["GET"])(authenticate_token(get_profile))
user_bp.route("/reports/send", methods=["POST"])(send_report)