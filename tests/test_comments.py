import uuid
from extensions import db
from models.user_model import User

def unique_email():
    return f"commenttest_{uuid.uuid4().hex[:8]}@example.com"

def register_and_login(client):
    """Helper: creates a user and returns their JWT auth token."""
    email = unique_email()
    password = "TestPass123!"

    client.post("/auth/register", json={
        "name": "Comment Test User",
        "email": email,
        "password": password
    })

    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })

    token = response.get_json()["token"]
    return token

def create_post(client, token):
    """Helper: creates a post and returns its ID."""
    response = client.post("/posts",
        json={"title": "Post for Comments", "content": "Testing comments"},
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.get_json()["post"]["id"]


class TestCommentsIntegration:

    def test_create_comment_requires_auth(self, client):
        token = register_and_login(client)
        post_id = create_post(client, token)

        response = client.post(f"/posts/{post_id}/comments", json={
            "text": "No auth comment"
        })
        assert response.status_code in (401, 422)

    def test_create_comment_success(self, client):
        token = register_and_login(client)
        post_id = create_post(client, token)

        response = client.post(f"/posts/{post_id}/comments",
            json={"text": "Great post!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["text"] == "Great post!"
        assert body["post_id"] == post_id

    def test_create_comment_empty_text_fails(self, client):
        token = register_and_login(client)
        post_id = create_post(client, token)

        response = client.post(f"/posts/{post_id}/comments",
            json={"text": ""},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

    def test_create_comment_nonexistent_post_fails(self, client):
        token = register_and_login(client)

        response = client.post("/posts/999999/comments",
            json={"text": "Comment on missing post"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_get_comments_returns_list(self, client):
        token = register_and_login(client)
        post_id = create_post(client, token)

        client.post(f"/posts/{post_id}/comments",
            json={"text": "First comment"},
            headers={"Authorization": f"Bearer {token}"}
        )

        response = client.get(f"/posts/{post_id}/comments")
        assert response.status_code == 200
        comments = response.get_json()
        assert len(comments) >= 1
        assert all("text" in c for c in comments)

    def test_get_comments_nonexistent_post_fails(self, client):
        response = client.get("/posts/999999/comments")
        assert response.status_code == 404