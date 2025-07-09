"""
Data retrieval and field extraction utilities for Airbnb listings.
"""

import logging
from typing import Any, Dict, List, Optional

from .constants import CHECKBOX_FIELD_MAPPING, DATABASE_PATH
from .db_helpers import DatabaseManager

logger = logging.getLogger(__name__)


def get_listing_by_id(
    listing_id: int, database_path: str = DATABASE_PATH
) -> Optional[Dict[str, Any]]:
    """
    Retrieve listing information by ID from database.

    Args:
        listing_id: The listing ID to retrieve
        database_path: Path to the database file

    Returns:
        Dictionary containing listing information, or None if not found
    """
    try:
        with DatabaseManager(database_path) as db_manager:
            listing_data = db_manager.get_listing(listing_id)

            if listing_data is None:
                logger.warning(f"Listing {listing_id} not found")
                return None

            # Add empty notes if not present
            if "notes" not in listing_data:
                listing_data["notes"] = ""

            return listing_data

    except Exception as e:
        logger.error(f"Error retrieving listing {listing_id}: {e}")
        return None


def get_listings_by_location(
    location: str, database_path: str = DATABASE_PATH
) -> List[Dict[str, Any]]:
    """
    Retrieve all listings from a specific location.

    Args:
        location: Location name to search for
        database_path: Path to the database file

    Returns:
        List of dictionaries containing listing information
    """
    try:
        with DatabaseManager(database_path) as db_manager:
            all_listings = db_manager.get_all_listings()

            # Filter by location (case-insensitive partial match)
            filtered_listings: List[Dict[str, Any]] = []

            for listing in all_listings:
                if location.lower() in listing.get("location", "").lower():
                    filtered_listings.append(listing)

            return filtered_listings

    except Exception as e:
        logger.error(f"Error searching by location: {e}")
        return []


def extract_field_from_listing(field_name: str, listing: Dict[str, Any]) -> Any:
    """
    Extract specific field from listing data with calculated fields support.

    Args:
        field_name: Name of the field to extract (from CHECKBOX_FIELD_MAPPING keys)
        listing: Dictionary containing listing data

    Returns:
        The requested field value

    Raises:
        KeyError: If field_name is not in CHECKBOX_FIELD_MAPPING
    """
    if field_name not in CHECKBOX_FIELD_MAPPING:
        raise KeyError(f"Unknown field: {field_name}")

    field_key = CHECKBOX_FIELD_MAPPING[field_name]

    # Handle calculated fields
    if field_key == "cost":
        return listing.get("cost", 0)
    elif field_key == "cover":
        return listing["images"][0] if listing["images"] else ""
    else:
        return listing.get(field_key, "")


def get_available_fields() -> List[str]:
    """
    Get list of all available fields for data extraction.

    Returns:
        List of field names that can be used with extract_field_from_listing
    """
    return list(CHECKBOX_FIELD_MAPPING.keys())


def get_all_listings(database_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """
    Retrieve all listings from the database.

    Args:
        database_path: Path to the database file

    Returns:
        List of dictionaries containing listing information
    """
    try:
        with DatabaseManager(database_path) as db_manager:
            return db_manager.get_all_listings()

    except Exception as e:
        logger.error(f"Error retrieving all listings: {e}")
        return []


def get_listing_count(database_path: str = DATABASE_PATH) -> int:
    """
    Get the total number of listings in the database.

    Args:
        database_path: Path to the database file

    Returns:
        Total number of listings
    """
    try:
        with DatabaseManager(database_path) as db_manager:
            return db_manager.get_listing_count()

    except Exception as e:
        logger.error(f"Error getting listing count: {e}")
        return 0


def delete_listing(listing_id: int, database_path: str = DATABASE_PATH) -> bool:
    """
    Delete a listing from the database.

    Args:
        listing_id: ID of the listing to delete
        database_path: Path to the database file

    Returns:
        True if listing was deleted, False if not found
    """
    try:
        with DatabaseManager(database_path) as db_manager:
            return db_manager.delete_listing(listing_id)

    except Exception as e:
        logger.error(f"Error deleting listing {listing_id}: {e}")
        return False


def listing_exists(listing_id: int, database_path: str = DATABASE_PATH) -> bool:
    """
    Check if a listing exists in the database.

    Args:
        listing_id: ID of the listing to check
        database_path: Path to the database file

    Returns:
        True if listing exists, False otherwise
    """
    try:
        with DatabaseManager(database_path) as db_manager:
            return db_manager.listing_exists(listing_id)

    except Exception as e:
        logger.error(f"Error checking listing {listing_id}: {e}")
        return False
