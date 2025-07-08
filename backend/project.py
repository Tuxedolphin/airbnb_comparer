"""
Airbnb Listing Scraper and Database Manager

This module provides functionality for scraping Airbnb listings, processing the data,
and storing it in a SQLite database for comparison purposes.
"""

import json
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pyairbnb  # type: ignore

# Constants
DATABASE_PATH = "./db/database.db"

# Field mappings for UI checkboxes
CHECKBOX_FIELD_MAPPING = {
    "ID": "id",
    "Rating": "average_rating",
    "URL": "url",
    "Duration": "duration",
    "Location": "location",
    "Coordinates": "coordinates",
    "Getting Around": "getting_around",
    "Check In/ Out Timing": "check_in_out",
    "Layout": "layout",
    "Capacity": "capacity",
    "Cost": "cost",
    "Super Host": "super_host",
    "Amenities": "amenities",
    "Notes": "notes",
    "Images": "images",
    "Cover": "cover",
}

TABLE = """
        CREATE TABLE IF NOT EXISTS main (
            id INTEGER PRIMARY KEY,
            url TEXT,
            json TEXT,
            duration INTEGER
        )
    """


# ================================
# URL Processing Functions
# ================================


def extract_from_url(link: str) -> Tuple[int, int, str, str, int]:
    """
    Extract listing ID and stay duration from Airbnb URL.

    Args:
        link: Airbnb listing URL containing check-in/check-out dates

    Returns:
        Tuple of (listing_id, stay_duration_in_days)

    Raises:
        ValueError: If URL format is invalid or dates are inconsistent
    """
    # Extract ID, check-in, and check-out dates from URL
    pattern = (
        r"^https://www\.airbnb\.com(?:\.sg)?/rooms/(\d+)\?"
        r".*check_in=(.{10}).*check_out=(.{10})"
        r".*adults=(\d+)"
    )
    match = re.search(pattern, link)

    if not match:
        raise ValueError("Invalid Airbnb URL format")

    listing_id = int(match.group(1))
    check_in_str: str = match.group(2)
    check_out_str: str = match.group(3)
    adults_count = int(match.group(4))

    # Parse dates
    try:
        check_in = datetime.fromisoformat(check_in_str)
        check_out = datetime.fromisoformat(check_out_str)

    except ValueError as e:
        raise ValueError(f"Invalid date format in URL: {e}")

    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date")

    # Calculate stay duration in days
    stay_duration = (check_out - check_in).days

    return listing_id, stay_duration, check_in_str, check_out_str, adults_count


# ================================
# Data Processing Functions
# ================================


def _calculate_average_rating(rating_data: Dict[str, Any]) -> float:
    """Calculate average rating excluding review count."""
    ratings = [
        float(value) for key, value in rating_data.items() if key != "review_count"
    ]

    return round(sum(ratings) / len(ratings), 2) if ratings else 0.0


def _extract_amenities(amenities_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Extract and organize amenities data."""
    amenities = {}

    for entry in amenities_data:
        amenity_title = entry["title"]
        amenity_values = [item["title"] for item in entry["values"]]
        amenities[amenity_title] = amenity_values

    return amenities


def _extract_location_info(
    location_descriptions: List[Dict[str, Any]],
) -> Tuple[str, str]:
    """Extract location and getting around information."""
    if len(location_descriptions) != 2:
        raise ValueError(
            f"Expected 2 location descriptions, got {len(location_descriptions)}"
        )

    location = ""
    getting_around = ""

    for description in location_descriptions:
        title = description["title"].lower()
        if title == "getting around":
            getting_around = description["content"].replace("<br />", "\n")
        else:
            location = description["title"].replace("\u014d", "o")

    return location, getting_around


def _process_listing_data(
    data: Dict[str, Any], listing_id: int, link: str, stay_length: int, costs: List[int]
) -> Dict[str, Any]:
    """Process raw scraped data into structured format."""
    info = {
        "id": listing_id,
        "url": link,
        "duration": stay_length,
        "daily_cost": costs[0],
        "misc_cost": costs[1],
    }

    # Basic information
    info["coordinates"] = json.dumps(data["coordinates"])
    info["super_host"] = data["is_super_host"]
    info["capacity"] = data["person_capacity"]

    # Calculate average rating
    info["average_rating"] = _calculate_average_rating(data["rating"])

    # Check in/out information
    info["check_in_out"] = [
        item["title"] for item in data["house_rules"]["general"][0]["values"]
    ]

    # Layout information
    info["layout"] = [data["sub_description"]["items"]]

    # Amenities
    info["amenities"] = _extract_amenities(data["amenities"])

    # Images
    info["images"] = [img["url"] for img in data["images"]]

    # Location information
    location, getting_around = _extract_location_info(data["location_descriptions"])
    info["location"] = location
    info["getting_around"] = getting_around

    return info


# ================================
# Main Functions
# ================================


def add_listing(link: str, costs: List[int], currency: str = "SGD") -> None:
    """
    Scrape Airbnb listing and store in database.

    Args:
        link: Airbnb listing URL
        costs: List containing [daily_cost, misc_cost]
        currency: Currency code for scraping (default: SGD)

    Raises:
        ValueError: If link is invalid or costs list doesn't have exactly 2 elements
    """
    print("Starting listing scrape...")

    # Extract listing ID and stay duration from URL
    listing_id, stay_length, check_in_str, check_out_str, adults_count = (
        extract_from_url(link)
    )

    # Scrape listing data from Airbnb
    data: Dict[str, Any] = pyairbnb.get_details(  # type: ignore
        room_url=link,
        currency=currency,
        check_in=check_in_str,
        check_out=check_out_str,
        adults=adults_count,
    )

    # Save raw data for debugging (optional)
    with open("result.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # Process and structure the data
    processed_info = _process_listing_data(data, listing_id, link, stay_length, costs)

    print("Data processing completed")

    # Initialize database tables if they don't exist
    create_tables(DATABASE_PATH)

    # Save to database
    add_entry_to_database(DATABASE_PATH, processed_info)

    print(f"Listing {listing_id} successfully added to database")


# ================================
# Data Retrieval Functions
# ================================


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
    conn = create_connection(database_path)

    try:
        with conn:
            cursor = conn.cursor()

            # Get JSON data
            cursor.execute("SELECT json FROM json WHERE listing_id = ?", (listing_id,))
            json_row = cursor.fetchone()

            if not json_row:
                print(f"Listing {listing_id} not found")
                return None

            # Get notes
            cursor.execute(
                "SELECT notes FROM others WHERE listing_id = ?", (listing_id,)
            )
            notes_row = cursor.fetchone()

            # Parse and combine data
            listing_data = json.loads(json_row[0])
            listing_data["notes"] = notes_row[0] if notes_row else ""

            return listing_data

    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"Error retrieving listing {listing_id}: {e}")
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
    conn = create_connection(database_path)

    try:
        with conn:
            cursor = conn.cursor()

            # Search for listings by location (case-insensitive partial match)
            cursor.execute(
                "SELECT listing_id FROM basic_info WHERE LOWER(location) LIKE LOWER(?)",
                (f"%{location}%",),
            )

            listing_ids = [row[0] for row in cursor.fetchall()]

        # Get full data for each listing
        listings = []
        for listing_id in listing_ids:
            listing = get_listing_by_id(listing_id, database_path)
            if listing is not None:
                listings.append(listing)
        return listings

    except sqlite3.Error as e:
        print(f"Error searching by location: {e}")
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
        return int(listing["daily_cost"]) * listing["duration"] + int(
            listing["misc_cost"]
        )
    elif field_key == "cover":
        return listing["images"][0] if listing["images"] else ""
    else:
        return listing.get(field_key, "")


# ================================
# Database Management Functions
# ================================


def create_connection(database_path: str) -> sqlite3.Connection:
    """
    Create a database connection to SQLite database.

    Args:
        database_path: Path to the database file

    Returns:
        SQLite connection object

    Raises:
        Exception: If connection fails
    """
    try:
        conn = sqlite3.connect(database_path)
        return conn
    except sqlite3.Error as e:
        raise Exception(f"SQLite connection error: {e}")


def create_table(conn: sqlite3.Connection, create_table_sql: str) -> None:
    """
    Create a table using the provided SQL statement.

    Args:
        conn: SQLite connection object
        create_table_sql: SQL CREATE TABLE statement

    Raises:
        Exception: If table creation fails
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
    except sqlite3.Error as e:
        raise Exception(f"Error creating table: {e}")


def create_tables(database_path: str) -> None:
    """
    Create all required tables in the database.

    Args:
        database_path: Path to the database file
    """

    conn = create_connection(database_path)

    try:
        with conn:
            create_table(conn, TABLE)
        print("Database tables created successfully")

    except Exception as e:
        print(f"Error creating tables: {e}")


def add_entry_to_database(database_path: str, listing_data: Dict[str, Any]) -> None:
    """
    Add a listing entry to the database.

    Args:
        database_path: Path to the database file
        listing_data: Dictionary containing listing information
    """
    conn = create_connection(database_path)

    try:
        with conn:
            cursor = conn.cursor()
            listing_id = listing_data["id"]

            # Insert into main tables (ignore duplicates)
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO main (id) VALUES (?)", (listing_id,)
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO basic_info (listing_id) VALUES (?)",
                    (listing_id,),
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO others (listing_id) VALUES (?)",
                    (listing_id,),
                )
            except sqlite3.Error as e:
                print(f"Warning: Error inserting base records: {e}")

            # Update each field
            for column, value in listing_data.items():
                if column == "id":
                    continue

                table = _get_table_for_column(column)

                # Determine ID column name
                id_column = "id" if table == "main" else "listing_id"

                # Update the field
                query = f"UPDATE {table} SET {column} = ? WHERE {id_column} = ?"
                cursor.execute(query, (json.dumps(value), listing_id))

            # Store complete JSON representation
            cursor.execute(
                "INSERT OR REPLACE INTO json (listing_id, json) VALUES (?, ?)",
                (listing_id, json.dumps(listing_data)),
            )

        print(f"Successfully saved listing {listing_id} to database")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# ================================
# Utility Functions
# ================================


def get_available_fields() -> List[str]:
    """
    Get list of all available fields for data extraction.

    Returns:
        List of field names that can be used with extract_field_from_listing
    """
    return list(CHECKBOX_FIELD_MAPPING.keys())


def validate_listing_data(listing_data: Dict[str, Any]) -> bool:
    """
    Validate that listing data contains required fields.

    Args:
        listing_data: Dictionary containing listing information

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["id", "url", "duration", "daily_cost", "misc_cost"]
    return all(field in listing_data for field in required_fields)


# ================================
# Legacy Function Aliases (for backward compatibility)
# ================================


def sql_get(listing_id: int) -> Optional[Dict[str, Any]]:
    """Legacy alias for get_listing_by_id."""
    return get_listing_by_id(listing_id)


def retrieve_from_location(
    location: str, database_path: str = DATABASE_PATH
) -> List[Dict[str, Any]]:
    """Legacy alias for get_listings_by_location."""
    return get_listings_by_location(location, database_path)


def retrieve_from_json(column: str, listing: Dict[str, Any]) -> Any:
    """Legacy alias for extract_field_from_listing."""
    return extract_field_from_listing(column, listing)


if __name__ == "__main__":
    print("Airbnb Listing Scraper and Database Manager")
    print("Available fields:", get_available_fields())
