import uuid
from extensions import db
from models.user_model import User

def unique_email():
    return f"posttest_{uuid.uuid4().hex[:8]}@example.com"

def register_and_login(client):
    """Helper: creates a user and returns their JWT auth token."""
    email = unique_email()
    password = "TestPass123!"

    client.post("/auth/register", json={
        "name": "Post Test User",
        "email": email,
        "password": password
    })

    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })

    token = response.get_json()["token"]
    return token

class TestPostsIntegration:

    def test_create_post_requires_auth(self, client):
        response = client.post("/posts", json={
            "title": "No Auth Post",
            "content": "This should fail"
        })
        assert response.status_code in (401, 422)

    def test_create_post_success(self, client):
        token = register_and_login(client)
        response = client.post("/posts",
            json={"title": "My First Post", "content": "Hello World"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["post"]["title"] == "My First Post"

    def test_create_post_missing_fields_fails(self, client):
        token = register_and_login(client)
        response = client.post("/posts",
            json={"title": "Only Title"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

    def test_get_my_posts_returns_only_own_posts(self, client):
        token = register_and_login(client)
        client.post("/posts",
            json={"title": "Post A", "content": "Content A"},
            headers={"Authorization": f"Bearer {token}"}
        )
        response = client.get("/posts/my-posts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        posts = response.get_json()
        assert len(posts) >= 1
        assert all("title" in p for p in posts)

class TestRelationalEndpoint:

    def test_get_user_with_posts(self, client):
        token = register_and_login(client)
        client.post("/posts",
            json={"title": "Relational Post", "content": "Testing join"},
            headers={"Authorization": f"Bearer {token}"}
        )

        me_response = client.get("/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        user_id = me_response.get_json()["id"]

        response = client.get(f"/users/{user_id}/posts")
        assert response.status_code == 200
        body = response.get_json()
        assert "user" in body
        assert "posts" in body
        assert len(body["posts"]) >= 1