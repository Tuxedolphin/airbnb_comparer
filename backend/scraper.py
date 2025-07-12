"""
Web scraping utilities for Airbnb listings.
"""

import logging
from typing import Any, Dict

import pyairbnb  # type: ignore

from .constants import DATABASE_PATH, DEFAULT_CURRENCY
from .data_processor import process_listing_data, validate_listing_data
from .db_helpers import DatabaseManager
from .url_utils import extract_from_url

logger = logging.getLogger(__name__)


def scrape_listing_data(
    room_id: int,
    check_in_str: str,
    check_out_str: str,
    adults_count: int,
    currency: str = DEFAULT_CURRENCY,
) -> Dict[str, Any]:
    """
    Scrape listing data from Airbnb using pyairbnb.

    Args:
        room_id: Airbnb listing ID
        check_in_str: Check-in date string
        check_out_str: Check-out date string
        adults_count: Number of adults
        currency: Currency code for scraping

    Returns:
        Dictionary containing scraped listing data

    Raises:
        Exception: If scraping fails
    """
    logger.info(
        f"Scraping listing data for: {room_id}, check_in: {check_in_str}, check_out: {check_out_str}, adults: {adults_count}, currency: {currency}"
    )

    try:
        data: Dict[str, Any] = pyairbnb.get_details(  # type: ignore
            room_id=room_id,
            currency=currency,
            check_in=check_in_str,
            check_out=check_out_str,
            adults=adults_count,
        )

        logger.debug(f"Successfully scraped {len(data)} fields from Airbnb")

        return data

    except Exception as e:
        logger.exception(f"Failed to scrape listing data from {room_id}: {e}")
        return {}


def add_listing(
    link: str,
    currency: str = DEFAULT_CURRENCY,
    database_path: str = DATABASE_PATH,
) -> None:
    """
    Scrape Airbnb listing and store in database.

    Args:
        link: Airbnb listing URL
        currency: Currency code for scraping (default: SGD)
        database_path: Path to the database file

    Raises:
        ValueError: If link is invalid or costs list doesn't have exactly 2 elements
        Exception: If scraping or database operations fail
    """

    logger.info(f"Starting listing addition process for URL: {link}")
    logger.debug(f"Parameters - Currency: {currency}, Database: {database_path}")

    try:
        # Extract listing ID and stay duration from URL
        logger.info("Extracting listing information from URL...")
        listing_id, stay_length, check_in_str, check_out_str, adults_count = (
            extract_from_url(link)
        )

        # Scrape listing data from Airbnb
        logger.info("Scraping listing data from Airbnb...")
        data = scrape_listing_data(
            listing_id, check_in_str, check_out_str, adults_count, currency
        )

        # Process and structure the data
        logger.info("Processing scraped data...")
        processed_info = process_listing_data(data, listing_id, link, stay_length)
        logger.debug(f"Processed data contains {len(processed_info)} fields")

        # Validate the processed data
        logger.info("Validating processed data...")
        if not validate_listing_data(processed_info):
            logger.exception(
                "Data validation failed - processed listing data is invalid"
            )
            raise ValueError("Processed listing data is invalid")

        logger.info("Data validation successful")

    except Exception as e:
        logger.exception(f"Failed during data extraction/processing phase: {e}")
        raise

    # Save to database
    logger.info("Saving listing to database...")
    try:
        with DatabaseManager(database_path) as db_manager:
            logger.debug("Database connection established")

            # Create tables if they don't exist
            db_manager.create_tables()
            logger.debug("Database tables verified/created")

            # Add the listing
            db_manager.add_entry(processed_info)
            logger.debug("Listing entry added to database")

        logger.info(f"Listing {listing_id} successfully added to database")

    except Exception as e:
        logger.exception(f"Failed to save listing {listing_id} to database: {e}")
        raise Exception(f"Failed to save listing to database: {e}")


def update_listing_costs(
    listing_id: int, new_cost: int, database_path: str = DATABASE_PATH
) -> bool:
    """
    Update the costs for an existing listing.

    Args:
        listing_id: ID of the listing to update
        new_cost: Total cost for the listing
        database_path: Path to the database file

    Returns:
        True if update was successful, False otherwise
    """

    logger.info(f"Starting cost update for listing {listing_id}")
    logger.debug(f"Parameters - New cost: {new_cost}, Database: {database_path}")

    try:
        with DatabaseManager(database_path) as db_manager:
            logger.debug("Database connection established for cost update")

            logger.info(f"Retrieving existing data for listing {listing_id}")
            listing_data = db_manager.get_listing(listing_id)

            if listing_data is None:
                logger.warning(f"Listing {listing_id} not found in database")
                return False

            logger.info(f"Found existing listing data for {listing_id}")
            logger.debug(
                f"Updating cost from {listing_data.get('cost', 'unknown')} to {new_cost}"
            )

            listing_data["cost"] = new_cost

            logger.debug("Saving updated listing data to database")
            db_manager.add_entry(listing_data)

            logger.info(f"Successfully updated costs for listing {listing_id}")
            return True

    except Exception as e:
        logger.exception(f"Error updating listing {listing_id}: {e}")
        return False
