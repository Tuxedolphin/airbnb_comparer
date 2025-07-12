"""
Airbnb Listing Scraper and Database Manager - Main Entry Point

This script provides the main entry point for the Airbnb listing scraper application.
Run this script to initialize the database and display system status.

Usage:
    python -m backend.main
    # or
    python backend/main.py
"""

import logging

from .constants import DATABASE_PATH
from .data_retrieval import get_available_fields
from .db_helpers import DatabaseManager
from .logging_config import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""

    setup_logging()

    logger.info("Airbnb Listing Scraper and Database Manager")
    logger.info(f"Available fields: {get_available_fields()}")
    logger.info(f"Database path: {DATABASE_PATH}")

    # Initialize database
    try:
        with DatabaseManager(DATABASE_PATH) as db_manager:
            db_manager.create_tables()
            count = db_manager.get_listing_count()
            logger.info(f"Current listings in database: {count}")

    except Exception as e:
        logger.exception(f"Error initializing database: {e}")


if __name__ == "__main__":
    main()
