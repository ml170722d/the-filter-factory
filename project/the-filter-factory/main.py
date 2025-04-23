import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete

from modules.db import init_db, create_all_tables, db, DenyList, AllowList

load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

app = Flask(__name__)

init_db(app)
create_all_tables(app)

# actuator
@app.route("/health", methods=["GET"])
def health():
    try:
        db.session.execute(select(1))
        return {"status": "UP"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "DOWN"}, 500


# GET methods
@app.route("/denylist", methods=["GET"])
def get_denylist():
    # Handle GET request to retrieve denylist
    denylist = DenyList.query.all()
    urls = [entry.url for entry in denylist]
    return jsonify(urls), 200


@app.route("/allowlist", methods=["GET"])
def get_allowlist():
    # Handle GET request to retrieve allowlist
    allowlist = AllowList.query.all()
    urls = [entry.url for entry in allowlist]
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

        existing_urls = [str(url) for url in db.session.execute(
            select(AllowList.url).where(AllowList.url.in_(data))
        ).scalars().all()]
        # logger.debug(f"Existing urls: {existing_urls}")

        new_urls = list(set(data) - set(existing_urls))
        # logger.debug(f"New urls: {new_urls}")

        #  Remove new urls from denylist
        db.session.execute(delete(DenyList).where(DenyList.url.in_(new_urls)))

        entries = [AllowList(url=url) for url in new_urls]
        db.session.add_all(entries)
        db.session.commit()

        result = new_urls + existing_urls
        logger.debug(result)
        return jsonify({
            "urls_added": result,
            "message": "URLs added to the allowlist"
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"DB error in /allowlist: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in /allowlist: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/denylist", methods=["POST"])
def add_to_denylist():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({
                "message": "Data sent must be string array"
            }), 400

        existing_urls = [str(url) for url in db.session.execute(
            select(DenyList.url).where(DenyList.url.in_(data))
        ).scalars().all()]
        # logger.debug(f"Existing urls: {existing_urls}")

        new_urls = list(set(data) - set(existing_urls))
        # logger.debug(f"New urls: {new_urls}")

        #  Remove new urls from allowlist
        db.session.execute(delete(AllowList).where(AllowList.url.in_(new_urls)))

        entries = [DenyList(url=url) for url in new_urls]
        db.session.add_all(entries)
        db.session.commit()

        result = new_urls + existing_urls
        logger.debug(result)
        return jsonify({
            "urls_added": result,
            "message": "URLs added to the allowlist"
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"DB error in /allowlist: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in /allowlist: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Error handeling
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception occurred")
    return jsonify({"error": "Something went wrong"}), 500


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
