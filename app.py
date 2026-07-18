from flask import Flask
from routes.user_routes import user_bp
from middleware.error_handler import register_error_handlers
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Flask!"

app.register_blueprint(user_bp)
register_error_handlers(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)