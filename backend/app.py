import os
from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from backend.models import init_db


def create_app(config_class=None):
    """Application factory for CivicPulse."""
    app = Flask(__name__)

    if config_class is None:
        env = os.environ.get("FLASK_ENV", "development").lower()
        if env == "production":
            config_class = ProductionConfig
        elif env == "testing":
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig

    app.config.from_object(config_class)

    # Initialize Database
    init_db(app.config["SQLALCHEMY_DATABASE_URI"])

    # Enable CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
    )

    # Register Blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.issues import issues_bp
    from backend.routes.clusters import clusters_bp
    from backend.routes.analytics import analytics_bp
    from backend.routes.reports import reports_bp
    from backend.routes.storage import storage_bp
    from backend.routes.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(clusters_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(storage_bp)
    app.register_blueprint(health_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "An internal server error occurred"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"Starting CivicPulse backend server on {host}:{port}")
    app.run(host=host, port=port, debug=app.config.get("DEBUG", True))
