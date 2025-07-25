"""
Constants for the Airbnb Listing Scraper and Database Manager.
"""

from pathlib import Path

# Database configuration
DATABASE_DIR = Path("./db")
DATABASE_PATH = str(DATABASE_DIR / "database.db")

# Ensure database directory exists
DATABASE_DIR.mkdir(exist_ok=True)

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
    "Highlights": "highlights",
    "Reviews Summary": "reviews_summary",
    "House Rules": "house_rules",
    "Property Details": "property_details",
    "Notes": "notes",
    "Images": "images",
    "Cover": "cover",
}

# Required fields for listing validation
REQUIRED_LISTING_FIELDS = ["id", "url", "cost"]

# Default scraping configuration
DEFAULT_CURRENCY = "SGD"
DEBUG_JSON_OUTPUT = "result.json"

# URL patterns
AIRBNB_ROOM_ID_PATTERN = r"^https://www\.airbnb\.com(?:\.sg)?/rooms/(\d+)"
AIRBNB_ADULTS_PATTERN = r"adults=(\d+)"
AIRBNB_CHECK_IN_PATTERN = r"check_in=([^&]+)"
AIRBNB_CHECK_OUT_PATTERN = r"check_out=([^&]+)"


# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
