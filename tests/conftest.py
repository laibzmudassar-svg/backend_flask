import pytest
from app import app as flask_app
from extensions import limiter


@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    limiter.enabled = False
    yield flask_app
    limiter.enabled = True


@pytest.fixture
def client(app):
    return app.test_client()