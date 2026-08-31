import eventlet
eventlet.monkey_patch()

from flask import Flask, g, request
from routes.user_routes import user_bp
from routes.post_routes import post_bp
from routes.health_routes import health_bp
import sockets
from middleware.error_handler import register_error_handlers
from extensions import db, migrate, limiter, socketio
from dotenv import load_dotenv
import os
from flask_talisman import Talisman
from flask_cors import CORS
from flasgger import Swagger
from logging_config import configure_logging
from prometheus_flask_exporter import PrometheusMetrics
import uuid


load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

# --- Payload Size Limit (protects against memory exhaustion attacks) ---
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

# --- Structured JSON Logging ---
configure_logging(app)

# --- Prometheus Metrics Exporter (exposes /metrics automatically) ---
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Backend Flask Application', version='1.0.0')

db.init_app(app)
migrate.init_app(app, db)
socketio.init_app(app)

swagger = Swagger(app)

# --- Content Security Policy ---
csp = {
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'"
}

Talisman(
    app,
    force_https=False,
    strict_transport_security=True,
    content_security_policy=csp,
    frame_options='DENY',
    x_content_type_options=True
)

CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

limiter.init_app(app)
limiter.default_limits = ["200 per day", "50 per hour"]

@app.before_request
def assign_correlation_id():
    g.correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))

@app.after_request
def add_correlation_id_header(response):
    response.headers['X-Correlation-ID'] = g.get('correlation_id', 'unknown')
    return response

from models.user_model import User
from models.post_model import Post


@app.route("/")
def home():
    app.logger.info(
        "Home route accessed",
        extra={"event": "home_hit", "correlation_id": g.correlation_id}
    )
    return "Welcome to Flask!"


app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
app.register_blueprint(health_bp)
register_error_handlers(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(app.url_map)
    socketio.run(app, debug=True, port=port, use_reloader=False)