"""
Airbnb Listing Scraper and Database Manager - Package Interface

This module provides the package interface for the Airbnb listing scraper.
It re-exports the main functions from various helper modules to provide
a clean, unified API.

Example usage:
    from backend import add_listing, get_listing_by_id, DatabaseManager

    # Add a listing
    add_listing(url, costs)

    # Retrieve a listing
    listing = get_listing_by_id(12345)

    # Direct database access
    with DatabaseManager(DATABASE_PATH) as db:
        db.create_tables()
"""

# Import all main functionality from helper modules
from .constants import CHECKBOX_FIELD_MAPPING, DATABASE_PATH
from .data_processor import validate_listing_data
from .data_retrieval import (
    delete_listing,
    extract_field_from_listing,
    get_all_listings,
    get_available_fields,
    get_listing_by_id,
    get_listing_count,
    get_listings_by_location,
    listing_exists,
)
from .db_helpers import DatabaseManager
from .scraper import add_listing, update_listing_costs
from .url_utils import extract_from_url, validate_airbnb_url

# Export main functions
__all__ = [
    # Main functions
    "add_listing",
    "get_listing_by_id",
    "get_listings_by_location",
    "get_all_listings",
    "get_listing_count",
    "delete_listing",
    "listing_exists",
    "extract_field_from_listing",
    "get_available_fields",
    "validate_listing_data",
    "update_listing_costs",
    # URL utilities
    "extract_from_url",
    "validate_airbnb_url",
    # Database manager
    "DatabaseManager",
    # Constants
    "CHECKBOX_FIELD_MAPPING",
    "DATABASE_PATH",
]
