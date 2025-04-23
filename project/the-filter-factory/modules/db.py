import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Integer, Text, DateTime, func
from pyctuator.health.db_health_provider import DbHealthProvider

load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")

# DB Health for Pyctuator
db_health_provider = DbHealthProvider(create_engine(DATABASE_URI, pool_pre_ping=True))

db = SQLAlchemy()

# DenyList model
class DenyList(db.Model):
    __tablename__ = "denylist"
    id = db.Column(Integer, primary_key=True)
    url = db.Column(Text, unique=True, nullable=False)
    date_added = db.Column(DateTime, default=func.current_timestamp())


# AllowList model
class AllowList(db.Model):
    __tablename__ = "allowlist"
    id = db.Column(Integer, primary_key=True)
    url = db.Column(Text, unique=True, nullable=False)
    date_added = db.Column(DateTime, default=func.current_timestamp())


# Initialize the database with the models
def create_all_tables(app: Flask):
    with app.app_context():
        db.create_all()


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)
