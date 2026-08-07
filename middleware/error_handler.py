from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": "Resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "success": False,
            "error": "Bad request"
        }), 400

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({
            "success": False,
            "error": f"Too many requests: {e.description}"
        }), 429

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
       
        return jsonify({
            "success": False,
            "error": e.description
        }), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
    
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500