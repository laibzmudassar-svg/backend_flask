from flask import Blueprint
from controllers.user_controller import create_user, get_user

user_bp = Blueprint("user_bp", __name__)

user_bp.route("/users", methods=["POST"])(create_user)
user_bp.route("/users/<int:user_id>", methods=["GET"])(get_user)