import datetime
import requests
import re
from loguru import logger
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from sqlalchemy import Sequence, select, delete, update
from sqlalchemy.exc import SQLAlchemyError

from modules.db import db, DenyList, AllowList

SESSION = requests.Session()
RETRIES = Retry(total=5, backoff_factor=0.5)
SESSION.mount("http://", HTTPAdapter(max_retries=RETRIES))
SESSION.mount("https://", HTTPAdapter(max_retries=RETRIES))

def _parse_urls_to_json(urls) -> list[str]:
    try:
        urls = urls.split("\n")
        urls_list = []
        for url in urls:
            if url.startswith("#") or url == "":
                continue
            else:
                urls_list.append(url.replace("\r", ""))
        return urls_list
    except Exception as e:
        logger.error(f"Error parsing URL list to JSON: {e}")
        return []

def get_url_list() -> list[str]:
    try:
        logger.info("Fetching URL list")
        response = SESSION.get("https://urlhaus.abuse.ch/downloads/text/")
        response.raise_for_status()
        urls = _parse_urls_to_json(response.text)
        return urls
    except requests.RequestException as e:
        logger.error(f"Error fetching URL list: {e}")
        return [], ''

def get_health() -> tuple[dict[str, str], int]:
    try:
        db.session.execute(select(1))
        return {"status": "UP"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "DOWN"}, 500

###

def update_danylist() -> list[str]:
    latest_urls = get_url_list()
    existing_urls = get_denylist(latest_urls)
    new_urls = list(set(latest_urls) - set(existing_urls))
    add_to_denylist(new_urls)

    # deleteurls that are not present in latest url list
    db.session.execute(
        delete(DenyList).where(DenyList.url.notin_(latest_urls))
    )
    db.session.commit()

    result = list(map(str, db.session.execute(
            select(DenyList.url).where(DenyList.url.notin_(
                select(AllowList.url)
            ))
        ).scalars().all()
    ))
    return result

def get_denylist(data: list[str]) -> list[str]:
    statement = None
    if data is None:
        statement = select(DenyList.url)
    else:
        statement = select(DenyList.url).where(DenyList.url.in_(data))

    result = db.session.execute(statement).scalars().all()
    return list(map(str, result))

def add_to_denylist(data: list[str]) -> list[str]:
    try:
        if not isinstance(data, list):
            return jsonify({
                "message": "Data sent must be string array"
            }), 400

        existing_urls = get_denylist(data)

        new_urls = list(set(data) - set(existing_urls))

        entries = [DenyList(url=url) for url in new_urls]
        db.session.add_all(entries)
        db.session.commit()

        result = new_urls + existing_urls

        return result

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"DB error in /allowlist: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /allowlist: {e}")
        raise e

def remove_from_denylist(data: list[str] = None) -> None:
    if data is None:
        return
    db.session.execute(delete(DenyList).where(DenyList.url.in_(data)))
    db.session.commit()

###

def get_allowlist(data: list[str] = None) -> list[str]:
    statement = None
    if data is None:
        statement = select(AllowList.url)
    else:
        statement = select(AllowList.url).where(AllowList.url.in_(data))

    result = db.session.execute(statement).scalars().all()
    return list(map(str, result))

def add_to_allowlist(data: list[str]) -> list[str]:
    try:
        if not isinstance(data, list):
            return jsonify({
                "message": "Data sent must be string array"
            }), 400

        existing_urls = get_allowlist(data)
        # logger.debug(len(data))

        new_urls = list(set(data) - set(existing_urls))
        logger.debug(len(new_urls))

        entries = [AllowList(url=url) for url in new_urls]
        db.session.add_all(entries)
        db.session.commit()

        result = new_urls + existing_urls
        logger.debug(sorted(result) == sorted(data))

        return result

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"DB error in /allowlist: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in /allowlist: {e}")
        raise e

def remove_from_allowlist(data: list[str] = None) -> None:
    if data is None:
        return
    db.session.execute(delete(AllowList).where(AllowList.url.in_(data)))
    db.session.commit()
