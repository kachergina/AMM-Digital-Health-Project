"""AMM Digital System — Flask application entry point.

This file creates the Flask app and wires the API routes. It is the main
entry point for the digital system.

Run it locally with:

    python3 app.py

Then open http://127.0.0.1:5001/ for the dashboard, and the API at
http://127.0.0.1:5001/api/vitals and /api/status.
"""

from flask import Flask
import os

from api.routes import api_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    """Build and return the Flask application.

    Templates and static files live in dashboard/ so the dashboard stays
    separate from the existing AMM website assets. Paths are absolute so the
    app works no matter which folder it is launched from.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "dashboard", "templates"),
        static_folder=os.path.join(BASE_DIR, "dashboard", "static"),
    )
    app.register_blueprint(api_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
