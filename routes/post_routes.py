from flask import Blueprint
from controllers.post_controller import (
    create_post,
    update_post,
    get_my_posts,
    get_user_with_posts,
    get_users_with_posts_raw_join,
    get_all_users_with_posts_left_join,
    search_posts_by_title
)
from middleware.auth_middleware import authenticate_token

post_bp = Blueprint("post_bp", __name__)

post_bp.route("/posts", methods=["POST"])(authenticate_token(create_post))

post_bp.route("/posts/<int:post_id>", methods=["PUT"])(authenticate_token(update_post))

post_bp.route("/posts/my-posts", methods=["GET"])(authenticate_token(get_my_posts))

post_bp.route("/users/<int:user_id>/posts", methods=["GET"])(get_user_with_posts)

post_bp.route("/posts/join/inner", methods=["GET"])(get_users_with_posts_raw_join)
post_bp.route("/posts/join/left", methods=["GET"])(get_all_users_with_posts_left_join)

post_bp.route("/posts/search", methods=["GET"])(search_posts_by_title)