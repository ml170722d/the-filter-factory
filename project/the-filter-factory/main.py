import os
from loguru import logger
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Import database initialization and business logic
from modules.db import init_db, create_all_tables
from modules.functions import (
    get_health,
    update_denylist as updateDl,
    get_allowlist as getAl,
    add_to_allowlist as addAl
)

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Host and port configured via environment
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

# Initialize database bindings and create tables if they don't exist
init_db(app)
create_all_tables(app)


@app.route("/health", methods=["GET"])
def health():
    """
    Actuator-style health endpoint.
    Returns UP if DB is reachable, DOWN otherwise.
    """
    return get_health()


@app.route("/denylist", methods=["GET"])
def get_denylist():
    """
    GET /denylist
    - Fetches fresh URLs from upstream, updates local DB
    - Returns the full denylist minus any allowlisted URLs
    """
    urls = updateDl()
    return jsonify(urls), 200


@app.route("/allowlist", methods=["GET"])
def get_allowlist():
    """
    GET /allowlist
    - Returns all URLs that have been added to the allowlist
    """
    urls = getAl()
    return jsonify(urls), 200


@app.route("/allowlist", methods=["POST"])
def add_to_allowlist():
    """
    POST /allowlist
    - Accepts a JSON array of URLs
    - Persists new URLs to the allowlist DB table
    - Returns the full set of allowlisted URLs
    """
    try:
        data = request.get_json()
        # Validate input type
        if not isinstance(data, list):
            return jsonify({"message": "Data sent must be string array"}), 400

        # Delegate to business logic
        result = addAl(data)

        return (
            jsonify({
                "urls_added": result,
                "message": "URLs added to the allowlist"
            }),
            201
        )

    except SQLAlchemyError as e:
        # Log DB-specific errors
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        # Fallback for any other errors
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """
    Global exception handler.
    Logs the exception and returns a 500 JSON error.
    """
    logger.exception(f"Unhandled exception occurred: {e}")
    return jsonify({"error": "Something went wrong"}), 500


if __name__ == "__main__":
    # Development server; in production use Gunicorn/Uvicorn
    app.run(host=HOST, port=PORT, debug=True)
