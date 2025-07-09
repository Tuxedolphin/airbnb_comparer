"""
Data processing utilities for Airbnb listing data.
"""

import json
import logging
from typing import Any, Dict, List, Tuple

from .constants import REQUIRED_LISTING_FIELDS
import re

logger = logging.getLogger(__name__)


def calculate_average_rating(rating_data: Dict[str, Any]) -> float:
    """
    Calculate average rating excluding review count.

    Args:
        rating_data: Dictionary containing rating information

    Returns:
        Average rating as a float, rounded to 2 decimal places

    Raises:
        ValueError: If rating_data is empty or contains no valid ratings
    """
    if not rating_data:
        raise ValueError("Rating data cannot be empty")

    ratings = [
        float(value)
        for key, value in rating_data.items()
        if key != "review_count" and isinstance(value, (int, float, str))
    ]

    if not ratings:
        logger.warning("No valid ratings found in rating data")
        return 0.0

    return round(sum(ratings) / len(ratings), 2)


def extract_amenities(amenities_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Extract and organize amenities data.

    Args:
        amenities_data: List of amenity dictionaries

    Returns:
        Dictionary with amenity categories as keys and lists of amenities as values

    Raises:
        ValueError: If amenities_data is not properly formatted
    """
    amenities: Dict[str, List[str]] = {}

    for entry in amenities_data:
        if "title" not in entry or "values" not in entry:

            logger.warning(f"Skipping malformed amenity entry: {entry}")
            continue

        amenity_title = str(entry["title"])

        try:
            amenity_values = [
                str(item["title"]) for item in entry["values"] if "title" in item
            ]
            amenities[amenity_title] = amenity_values

        except (KeyError, TypeError) as e:
            logger.warning(f"Error processing amenity values for {amenity_title}: {e}")

    return amenities


def extract_location_info(
    location_descriptions: List[Dict[str, Any]],
) -> Tuple[str, str]:
    """
    Extract location and getting around information.

    Args:
        location_descriptions: List of location description dictionaries

    Returns:
        Tuple of (location, getting_around)
    """
    location = ""
    getting_around = ""

    # Handle empty location descriptions
    if not location_descriptions:
        return location, getting_around

    for description in location_descriptions:
        if "title" not in description or "content" not in description:
            logger.warning(f"Skipping malformed location description: {description}")
            continue

        title = description["title"].lower()

        if title == "getting around":
            getting_around = description["content"].replace("<br />", "\n")
        elif title == "neighbourhood highlights":
            location = description["content"].replace("<br />", "\n")
        else:
            # Use the first description as location if not specifically categorized
            if not location:
                location = description["content"].replace("<br />", "\n")

    return location, getting_around


def extract_price(data: Dict[str, Any]) -> float:
    """
    Extract price from listing data.

    Args:
        data: Dictionary containing listing data with price information

    Returns:
        Price as a float, using discounted price if available, otherwise regular price

    """

    def extract_numeric_price(price_str: str) -> float:
        if not price_str:
            return 0.0

        # Remove currency symbols, commas, and extract numeric part
        numeric_match = re.search(r"[\d,]+\.?\d*", str(price_str))

        if numeric_match:
            return float(numeric_match.group().replace(",", ""))

        return 0.0

    try:
        price_data = data.get("price", {})
        main_price_data = price_data.get("main", {})

        # Try discounted price first, then regular price
        discounted_price = main_price_data.get("discountedPrice", "")
        regular_price = main_price_data.get("price", "")

        # Handle case where discounted_price might be an empty dict
        if isinstance(discounted_price, dict):
            discounted_price = ""
        if isinstance(regular_price, dict):
            regular_price = ""

        discounted_price_value = extract_numeric_price(discounted_price)
        regular_price_value = extract_numeric_price(regular_price)

        # Return discounted price if available, otherwise regular price
        return (
            discounted_price_value
            if discounted_price_value > 0
            else regular_price_value
        )

    except (TypeError, ValueError) as e:
        logger.warning(f"Error extracting price data: {e}")
        return 0.0


def process_listing_data(
    data: Dict[str, Any], listing_id: int, link: str, stay_length: int
) -> Dict[str, Any]:
    """
    Process raw scraped data into structured format.

    Args:
        data: Raw scraped data from Airbnb
        listing_id: Unique identifier for the listing
        link: Original Airbnb URL
        stay_length: Length of stay in days

    Returns:
        Dictionary containing processed listing information

    Raises:
        KeyError: If required fields are missing from data
    """
    # Extract price information
    total_cost = extract_price(data)

    info: Dict[str, Any] = {
        "id": listing_id,
        "url": link,
        "duration": stay_length,
        "cost": total_cost,
    }

    try:
        # Basic information
        info["coordinates"] = json.dumps(data["coordinates"])
        info["super_host"] = data["is_super_host"]
        info["capacity"] = data["person_capacity"]

        # Calculate average rating
        info["average_rating"] = calculate_average_rating(data["rating"])

        # Check in/out information - handle potential missing or empty structure
        check_in_out = []
        house_rules = data.get("house_rules", {})
        general_rules = house_rules.get("general", [])

        if general_rules:
            for rule_group in general_rules:
                if rule_group.get("title", "").lower() == "checking in and out":
                    check_in_out = [
                        item["title"]
                        for item in rule_group.get("values", [])
                        if "title" in item
                    ]
                    break

        info["check_in_out"] = check_in_out

        # Amenities
        info["amenities"] = extract_amenities(data.get("amenities", []))

        # Images
        info["images"] = [img["url"] for img in data.get("images", []) if "url" in img]

        # Location information
        location_descriptions = data.get("location_descriptions", [])
        location, getting_around = extract_location_info(location_descriptions)
        info["location"] = location
        info["getting_around"] = getting_around

        info["highlights"] = extract_highlights(data.get("highlights", []))
        info["reviews_summary"] = extract_reviews_summary(data.get("reviews", []))
        info["house_rules"] = extract_house_rules(house_rules)
        info["property_details"] = extract_property_details(data)

        return info

    except KeyError as e:
        logger.error(f"Missing required field in scraped data: {e}")
        raise KeyError(f"Missing required field in scraped data: {e}")

    except Exception as e:
        logger.error(f"Error processing listing data: {e}")
        raise


def extract_highlights(highlights_data: List[Dict[str, Any]]) -> List[str]:
    """
    Extract listing highlights/features.

    Args:
        highlights_data: List of highlight dictionaries

    Returns:
        List of dictionaries containing highlight information
    """
    highlights: List[str] = []

    for highlight in highlights_data:
        if "title" in highlight:
            highlights.append(highlight["title"])

    return highlights


def extract_reviews_summary(reviews_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract review summary statistics.

    Args:
        reviews_data: List of review dictionaries

    Returns:
        Dictionary containing review summary statistics
    """
    if not reviews_data:
        return {"total_reviews": 0, "recent_reviews": [], "languages": []}

    recent_reviews: List[Dict[str, str | int]] = []

    # Get first 5 reviews and collect languages
    for review in reviews_data[:5]:
        if "comments" in review and "rating" in review:
            recent_reviews.append(
                {
                    "comment": review["comments"],
                    "rating": review["rating"],
                    "date": review.get("localizedDate", ""),
                }
            )

    return {
        "total_reviews": len(reviews_data),
        "recent_reviews": recent_reviews,
    }


def extract_house_rules(house_rules_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract house rules information.

    Args:
        house_rules_data: Dictionary containing house rules

    Returns:
        Dictionary with organized house rules
    """
    rules: Dict[str, List[str]] = {
        "additional_rules": [house_rules_data.get("aditional", "")],
        "general_rules": [],
        "check_in_out": [],
    }

    # General rules
    general_rules = house_rules_data.get("general", [])

    for rule_group in general_rules:
        if "title" in rule_group and "values" in rule_group:
            title = rule_group["title"]
            values = [item["title"] for item in rule_group["values"] if "title" in item]

            if title.lower() == "checking in and out":
                rules["check_in_out"] = values

            else:
                rules["general_rules"].append({"category": title, "rules": values})

    return rules


def extract_property_details(data: Dict[str, Any]) -> Dict[str, str | bool | List[str]]:
    """
    Extract detailed property information.

    Args:
        data: Raw scraped data

    Returns:
        Dictionary containing property details
    """
    return {
        "room_type": data.get("room_type", ""),
        "is_guest_favorite": data.get("is_guest_favorite", False),
        "is_super_host": data.get("is_super_host", False),
        "layout": data.get("sub_description", {}).get("items", []),
    }


def validate_listing_data(listing_data: Dict[str, Any]) -> bool:
    """
    Validate that listing data contains required fields.

    Args:
        listing_data: Dictionary containing listing information

    Returns:
        True if valid, False otherwise
    """
    return all(field in listing_data for field in REQUIRED_LISTING_FIELDS)
