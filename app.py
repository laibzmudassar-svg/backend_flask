this is not valid python code !!!
from flask import Flask
from routes.user_routes import user_bp
from routes.post_routes import post_bp
import sockets
from middleware.error_handler import register_error_handlers
from extensions import db, migrate, limiter, socketio
from dotenv import load_dotenv
import os
from flask_talisman import Talisman
from flask_cors import CORS
from flasgger import Swagger
import eventlet
eventlet.monkey_patch()


load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

db.init_app(app)
migrate.init_app(app, db)
socketio.init_app(app)

swagger = Swagger(app)

# --- Security Headers (Helmet-equivalent) ---
Talisman(
    app,
    force_https=False,  # local dev pe HTTPS force nahi karna
    strict_transport_security=True,
    content_security_policy=None,
    frame_options='DENY',
    x_content_type_options=True
)

# --- CORS Restrictions (explicit origins, no wildcard) ---
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

# --- Rate Limiting ---
limiter.init_app(app)
limiter.default_limits = ["200 per day", "50 per hour"]

from models.user_model import User
from models.post_model import Post


@app.route("/")
def home():
    return "Welcome to Flask!"


app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
register_error_handlers(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, debug=True, port=port)