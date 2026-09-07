from flask import Blueprint
from controllers.comment_controller import create_comment, get_comments
from middleware.auth_middleware import authenticate_token

comment_bp = Blueprint("comment_bp", __name__)

comment_bp.route("/posts/<int:post_id>/comments", methods=["POST"])(
    authenticate_token(create_comment)
)
comment_bp.route("/posts/<int:post_id>/comments", methods=["GET"])(
    get_comments
)