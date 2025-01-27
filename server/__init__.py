"""Server package initialization."""

from .app import app

def create_app():
    """Create and configure the Flask application."""
    return app
