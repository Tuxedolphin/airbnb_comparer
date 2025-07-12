"""
URL processing utilities for Airbnb listing URLs.
"""

import re
from datetime import datetime
from typing import Tuple

from .constants import (
    AIRBNB_ROOM_ID_PATTERN,
    AIRBNB_ADULTS_PATTERN,
    AIRBNB_CHECK_IN_PATTERN,
    AIRBNB_CHECK_OUT_PATTERN,
)


def extract_from_url(link: str) -> Tuple[int, int, str, str, int]:
    """
    Extract listing information and booking details from an Airbnb URL.

    Parses an Airbnb listing URL to extract the listing ID, check-in and check-out dates,
    calculates the stay duration, and retrieves the number of adults. The function validates
    the URL format using a regex pattern and ensures dates are logically consistent.

        link (str): Airbnb listing URL containing listing ID, check-in/check-out dates,
                   and guest count parameters

        Tuple[int, int, str, str, int]: A tuple containing:
            - listing_id (int): Unique identifier for the Airbnb listing
            - stay_duration_in_days (int): Number of days between check-in and check-out
            - check_in_str (str): Check-in date in ISO format (YYYY-MM-DD)
            - check_out_str (str): Check-out date in ISO format (YYYY-MM-DD)
            - adults_count (int): Number of adult guests for the booking

        ValueError: If the URL format doesn't match the expected Airbnb pattern,
                   if date strings cannot be parsed as valid ISO dates,
                   or if check-out date is not after check-in date

    Example:
        >>> url = "https://www.airbnb.com/rooms/12345?check_in=2024-01-15&check_out=2024-01-20&adults=2"
        >>> extract_from_url(url)
        (12345, 5, '2024-01-15', '2024-01-20', 2)
    """

    # Extract room ID first
    room_id_match = re.search(AIRBNB_ROOM_ID_PATTERN, link)
    if not room_id_match:
        raise ValueError("Invalid Airbnb URL format - room ID not found")

    listing_id = int(room_id_match.group(1))

    # Extract adults parameter
    adults_match = re.search(AIRBNB_ADULTS_PATTERN, link)
    adults_count = int(adults_match.group(1)) if adults_match else 1

    # Extract check-in parameter
    check_in_match = re.search(AIRBNB_CHECK_IN_PATTERN, link)
    if not check_in_match:
        raise ValueError("Invalid Airbnb URL format - check_in parameter not found")

    check_in_str = check_in_match.group(1)

    # Extract check-out parameter
    check_out_match = re.search(AIRBNB_CHECK_OUT_PATTERN, link)
    if not check_out_match:
        raise ValueError("Invalid Airbnb URL format - check_out parameter not found")

    check_out_str = check_out_match.group(1)

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


def validate_airbnb_url(url: str) -> bool:
    """
    Validate if a URL is a valid Airbnb listing URL.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        extract_from_url(url)
        return True
    except ValueError:
        return False
