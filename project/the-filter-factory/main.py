import os
from loguru import logger
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from modules.db import init_db, create_all_tables
from modules.functions import get_health, \
    update_danylist as updateDl, \
    get_allowlist as getAl, \
    add_to_allowlist as addAl

load_dotenv()
app = Flask(__name__)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

init_db(app)
create_all_tables(app)

# actuator
@app.route("/health", methods=["GET"])
def health():
    return get_health()


# GET methods
@app.route("/denylist", methods=["GET"])
def get_denylist():
    urls = updateDl()
    return jsonify(urls), 200


@app.route("/allowlist", methods=["GET"])
def get_allowlist():
    urls = getAl()
    return jsonify(urls), 200


# POST methods
@app.route("/allowlist", methods=["POST"])
def add_to_allowlist():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({
                "message": "Data sent must be string array"
            }), 400

        result = addAl(data)

        return jsonify({
            "urls_added": result,
            "message": "URLs added to the allowlist"
        }), 201

    except SQLAlchemyError as e:
        logger.error(e)
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({"error": "Internal server error"}), 500


# Error handeling
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(f"Unhandled exception occurred: {e}")
    return jsonify({"error": "Something went wrong"}), 500


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
