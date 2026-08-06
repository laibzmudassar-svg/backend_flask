import json
from flask import request, jsonify, g, abort
from extensions import db, redis_client
from models.post_model import Post
from models.user_model import User
from sqlalchemy import text
from middleware.caching_middleware import cache_response
import bleach


def create_post():
    """Create a post, auto-assigned to the logged-in user (from JWT)."""
    data = request.get_json()

    if not data or "title" not in data or "content" not in data:
        abort(400, description="Missing title or content")

    clean_title = bleach.clean(data["title"], tags=[], strip=True)
    clean_content = bleach.clean(data["content"], tags=[], strip=True)

    user_id = g.user["userId"]

    post = Post(title=clean_title, content=clean_content, user_id=user_id)
    db.session.add(post)
    db.session.commit()

    # Invalidate cache since this user's post list has changed
    redis_client.delete(f"user:{user_id}:posts")
    redis_client.delete(f"user_posts:/users/{user_id}/posts:")

    return jsonify({
        "message": "Post created successfully",
        "post": post.to_dict()
    }), 201


def update_post(post_id):
    """Update a post and invalidate its related cache."""
    post = Post.query.get(post_id)

    if not post:
        abort(404, description="Post not found")

    data = request.get_json()

    if not data:
        abort(400, description="No data provided")

    if "title" in data:
        post.title = bleach.clean(data["title"], tags=[], strip=True)
    if "content" in data:
        post.content = bleach.clean(data["content"], tags=[], strip=True)

    db.session.commit()

    # Invalidate cache since this post's data has changed
    redis_client.delete(f"user:{post.user_id}:posts")
    redis_client.delete(f"user_posts:/users/{post.user_id}/posts:")

    return jsonify({
        "message": "Post updated successfully",
        "post": post.to_dict()
    }), 200


def get_my_posts():
    """User-bound endpoint: GET /posts/my-posts - only logged-in user's posts."""
    user_id = g.user["userId"]
    cache_key = f"user:{user_id}:posts"

    cached_posts = redis_client.get(cache_key)

    if cached_posts:
        print("Data coming from Redis Cache")
        return jsonify(json.loads(cached_posts)), 200

    posts = Post.query.filter_by(user_id=user_id).all()
    posts_data = [p.to_dict() for p in posts]

    redis_client.setex(
        cache_key,
        60,
        json.dumps(posts_data)
    )

    print("Data coming from Database")

    return jsonify(posts_data), 200


@cache_response(prefix="user_posts", ttl=300)
def get_user_with_posts(user_id):
    """ORM eager loading: GET /users/<id>/posts - user + their posts."""
    user = User.query.get(user_id)

    if not user:
        abort(404, description="User not found")

    return jsonify({
        "user": user.to_dict(),
        "posts": [p.to_dict() for p in user.posts]
    }), 200


def get_users_with_posts_raw_join():
    """Raw SQL INNER JOIN: combine users and posts manually."""
    sql = text("""
        SELECT users.id AS user_id, users.name, posts.id AS post_id, posts.title
        FROM users
        INNER JOIN posts ON users.id = posts.user_id
    """)
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]
    return jsonify(rows), 200


def get_all_users_with_posts_left_join():
    """Raw SQL LEFT JOIN: includes users with zero posts too."""
    sql = text("""
        SELECT users.id AS user_id, users.name, posts.id AS post_id, posts.title
        FROM users
        LEFT JOIN posts ON users.id = posts.user_id
    """)
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]
    return jsonify(rows), 200


def search_posts_by_title():
    """
    Raw SQL search with parameterized query - SAFE from SQL Injection.
    Query param: /posts/search?title=something
    """
    search_term = request.args.get("title", "")

    sql = text("""
        SELECT id, title, content, user_id
        FROM posts
        WHERE title LIKE :search_term
    """)

    result = db.session.execute(sql, {"search_term": f"%{search_term}%"})
    rows = [dict(row._mapping) for row in result]

    return jsonify(rows), 200