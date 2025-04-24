import requests
from loguru import logger
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from modules.db import db, DenyList, AllowList

# Configure a requests Session with retry/backoff logic
SESSION = requests.Session()
RETRIES = Retry(total=5, backoff_factor=0.5)
SESSION.mount("http://", HTTPAdapter(max_retries=RETRIES))
SESSION.mount("https://", HTTPAdapter(max_retries=RETRIES))


def _parse_urls_to_json(urls: str) -> list[str]:
    """
    Internal: Split raw text by newline, strip comments and empties,
    and return a clean list of URL strings.
    """
    try:
        lines = urls.split("\n")
        urls_list: list[str] = []
        for line in lines:
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Remove carriage returns and append
            urls_list.append(line.replace("\r", ""))
        return urls_list

    except Exception as e:
        logger.error(f"Error parsing URL list to JSON: {e}")
        return []


def get_url_list() -> list[str]:
    """
    Fetch the latest denylist from the external source.
    Returns a list of URL strings or an empty list on error.
    """
    try:
        logger.info("Fetching URL list from urlhaus.abuse.ch")
        response = SESSION.get("https://urlhaus.abuse.ch/downloads/text/")
        response.raise_for_status()
        return _parse_urls_to_json(response.text)

    except requests.RequestException as e:
        logger.error(f"Error fetching URL list: {e}")
        return []


def get_health() -> tuple[dict[str, str], int]:
    """
    Perform a simple DB ping to verify connectivity.
    Returns (payload, status_code).
    """
    try:
        # SELECT 1 to test connection
        db.session.execute(select(1))
        return {"status": "UP"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "DOWN"}, 500


def update_danylist() -> list[str]:
    """
    Fetch fresh URLs, sync the denylist table, prune stale entries,
    then return the effective denylist minus allowlisted URLs.
    """
    latest_urls = get_url_list()
    # Load what's already in DB for these URLs
    existing = get_denylist(latest_urls)
    # Compute new entries to insert
    new_entries = list(set(latest_urls) - set(existing))
    add_to_denylist(new_entries)

    # Remove any URLs no longer in the upstream feed
    db.session.execute(
        delete(DenyList).where(DenyList.url.notin_(latest_urls))
    )
    db.session.commit()

    # Return final denylist, excluding allowlist
    stmt = select(DenyList.url).where(
        DenyList.url.notin_(select(AllowList.url))
    )
    return list(map(str, db.session.execute(stmt).scalars().all()))


def get_denylist(data: list[str] | None = None) -> list[str]:
    """
    Retrieve denylist URLs from DB.
    If `data` is provided, only those URLs; otherwise all.
    """
    if data is None:
        stmt = select(DenyList.url)
    else:
        stmt = select(DenyList.url).where(DenyList.url.in_(data))
    return list(map(str, db.session.execute(stmt).scalars().all()))


def add_to_denylist(data: list[str]) -> list[str]:
    """
    Insert new URLs into denylist table.
    Returns the combined list of existing + newly added URLs.
    """
    try:
        existing = get_denylist(data)
        to_add = list(set(data) - set(existing))
        entries = [DenyList(url=url) for url in to_add]
        db.session.add_all(entries)
        db.session.commit()
        # Return full set
        return to_add + existing

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"DB error in add_to_denylist: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_to_denylist: {e}")
        raise


def remove_from_denylist(data: list[str] | None = None) -> None:
    """
    Remove specified URLs from the denylist table.
    """
    if not data:
        return
    db.session.execute(delete(DenyList).where(DenyList.url.in_(data)))
    db.session.commit()


def get_allowlist(data: list[str] | None = None) -> list[str]:
    """
    Retrieve allowlist URLs from DB.
    If `data` is provided, only those URLs; otherwise all.
    """
    if data is None:
        stmt = select(AllowList.url)
    else:
        stmt = select(AllowList.url).where(AllowList.url.in_(data))
    return list(map(str, db.session.execute(stmt).scalars().all()))


def add_to_allowlist(data: list[str]) -> list[str]:
    """
    Insert new URLs into allowlist table.
    Returns the combined list of existing + newly added URLs.
    """
    try:
        existing = get_allowlist(data)
        to_add = list(set(data) - set(existing))
        entries = [AllowList(url=url) for url in to_add]
        db.session.add_all(entries)
        db.session.commit()
        return to_add + existing

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"DB error in add_to_allowlist: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_to_allowlist: {e}")
        raise


def remove_from_allowlist(data: list[str] | None = None) -> None:
    """
    Remove specified URLs from the allowlist table.
    """
    if not data:
        return
    db.session.execute(delete(AllowList).where(AllowList.url.in_(data)))
    db.session.commit()
