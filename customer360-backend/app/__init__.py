"""
Flask Application Factory for Customer 360 Backend
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from app.routes.auth_routes import auth_bp
from app.routes.account_routes import account_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "customer360-frontend", "public")
    )
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    
    # Configure CORS to allow frontend communication from any local port (e.g., :3000, :5173)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "customer360-backend",
            "version": "1.0.0",
            "message": "Customer 360 Backend API is running."
        }), 200

    # Serve static frontend files if accessed via Flask port 5000
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": "Endpoint not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error occurred"
        }), 500

    return app
