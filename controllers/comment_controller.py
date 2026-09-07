import json
import bleach
from flask import request, jsonify, g, abort
from extensions import db, redis_client, task_queue
from models.comment_model import Comment
from models.post_model import Post
from schemas.comment_schema import CommentCreateSchema
from middleware.validation_middleware import validate_body
from events import publish_event
from tasks import notify_post_author


@validate_body(CommentCreateSchema)
def create_comment(post_id, validated_data=None):
    user_id = g.user["userId"]

    post = Post.query.get(post_id)
    if not post:
        abort(404, description="Post not found")

    clean_text = bleach.clean(validated_data.text, tags=[], strip=True)

    comment = Comment(
        text=clean_text,
        user_id=user_id,
        post_id=post_id
    )
    db.session.add(comment)
    db.session.commit()

    # Invalidate cached comments list for this post (data has changed)
    redis_client.delete(f"comments:post:{post_id}")

    # Publish domain event
    publish_event("comment_created", {
        "comment_id": comment.id,
        "post_id": post_id,
        "user_id": user_id
    })

    # Enqueue background job: notify post author (does not block the response)
    task_queue.enqueue(notify_post_author, post_id, comment.id)

    return jsonify(comment.to_dict()), 201


def get_comments(post_id):
    cache_key = f"comments:post:{post_id}"

    cached = redis_client.get(cache_key)
    if cached:
        print("Comments coming from Redis Cache")
        return jsonify(json.loads(cached)), 200

    post = Post.query.get(post_id)
    if not post:
        abort(404, description="Post not found")

    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    comments_data = [c.to_dict() for c in comments]

    redis_client.setex(cache_key, 60, json.dumps(comments_data))

    print("Comments coming from Database")

    return jsonify(comments_data), 200