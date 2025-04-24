import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Integer, Text, DateTime, func
from pyctuator.health.db_health_provider import DbHealthProvider

# Load DATABASE_URI from .env
load_dotenv()
DATABASE_URI = os.getenv("DATABASE_URI")

# Set up DB health-check provider for Pyctuator
db_health_provider = DbHealthProvider(
    create_engine(DATABASE_URI, pool_pre_ping=True)
)

# Initialize SQLAlchemy extension
db = SQLAlchemy()


class DenyList(db.Model):
    """
    ORM model for the denylist table.
    Stores malicious URLs with timestamp.
    """
    __tablename__ = "denylist"
    id = db.Column(Integer, primary_key=True)
    url = db.Column(Text, unique=True, nullable=False)
    date_added = db.Column(
        DateTime,
        default=func.current_timestamp(),
        nullable=False
    )


class AllowList(db.Model):
    """
    ORM model for the allowlist table.
    Stores URLs explicitly whitelisted by users.
    """
    __tablename__ = "allowlist"
    id = db.Column(Integer, primary_key=True)
    url = db.Column(Text, unique=True, nullable=False)
    date_added = db.Column(
        DateTime,
        default=func.current_timestamp(),
        nullable=False
    )


def create_all_tables(app: Flask):
    """
    Create all tables defined in the ORM if they don't exist.
    Called at startup.
    """
    with app.app_context():
        db.create_all()


def init_db(app: Flask):
    """
    Initialize SQLAlchemy with the Flask app.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    # Disable signal tracking to save memory (uncomment if needed)
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
