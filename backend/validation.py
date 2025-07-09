"""
Validation utilities for the Airbnb listing scraper.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_url_format(url: str) -> bool:
    """
    Validate if a string looks like a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if URL format is valid, False otherwise
    """
    if not url.strip():
        return False

    return url.startswith(("http://", "https://"))


def validate_listing_id(listing_id: Any) -> bool:
    """
    Validate listing ID format.

    Args:
        listing_id: Listing ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        return isinstance(listing_id, int) and listing_id > 0

    except (ValueError, TypeError):
        return False


def validate_required_fields(
    data: Dict[str, Any], required_fields: List[str]
) -> List[str]:
    """
    Check for missing required fields in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        List of missing field names (empty if all present)
    """

    missing_fields = [field for field in required_fields if field not in data]

    return missing_fields


def validate_database_path(path: Optional[str]) -> bool:
    """
    Validate database path format.

    Args:
        path: Database path to validate

    Returns:
        True if valid, False otherwise
    """
    if not path:
        return False

    # Basic path validation - should end with .db
    return path.strip().endswith(".db") and len(path.strip()) > 3


def sanitize_string(value: Any, max_length: int = 1000) -> str:
    """
    Sanitize and validate string input.

    Args:
        value: Value to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if value is None:
        return ""

    try:
        sanitized = str(value).strip()

        if len(sanitized) > max_length:
            logger.warning(
                f"String truncated from {len(sanitized)} to {max_length} characters"
            )
            sanitized = sanitized[:max_length]

        return sanitized

    except Exception as e:
        logger.error(f"Error sanitizing string: {e}")
        return ""


def validate_json_data(data: Any) -> bool:
    """
    Validate that data can be JSON serialized.

    Args:
        data: Data to validate

    Returns:
        True if JSON serializable, False otherwise
    """
    try:
        import json

        json.dumps(data)
        return True

    except (TypeError, ValueError) as e:
        logger.error(f"Data is not JSON serializable: {e}")
        return False
