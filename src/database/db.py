"""
Provides a database connection and session management for the application.

The `SQLALCHEMY_DATABASE_URL` constant holds the URL for the database connection, which is loaded from the application settings.

The `engine` object is a SQLAlchemy engine that manages the database connection pool.

The `SessionLocal` object is a SQLAlchemy session factory that can be used to create database sessions. Sessions are used to interact with the database, such as querying, inserting, updating, and deleting data.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
