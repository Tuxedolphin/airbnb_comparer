"""
Data processing utilities for Airbnb listing data.

This module provides functions to process and extract structured data from raw
Airbnb listing information. Functions are organized logically from utility functions
to main processing functions.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .constants import REQUIRED_LISTING_FIELDS

logger = logging.getLogger(__name__)


# ============================================================================
# Utility Functions
# ============================================================================


def _extract_numeric_price(price_str: str | int | float) -> float:
    """
    Extract numeric price value from string.

    Args:
        price_str: Price string potentially containing currency symbols

    Returns:
        Numeric price value
    """
    if not price_str:
        return 0.0

    # Convert to string if it's not already
    price_str = str(price_str)

    # Remove currency symbols, commas, and extract numeric part
    numeric_match = re.search(r"[\d,]+\.?\d*", price_str)

    if numeric_match:
        try:
            return float(numeric_match.group().replace(",", ""))
        except ValueError:
            logger.warning(f"Failed to convert price '{price_str}' to float")
            return 0.0

    return 0.0


def _clean_html_content(content: str) -> str:
    """
    Clean HTML content by replacing common HTML entities.

    Args:
        content: HTML content string

    Returns:
        Cleaned content string
    """
    if not content:
        return ""

    return content.replace("<br />", "\n").replace("&nbsp;", " ")


# ============================================================================
# Data Extraction Functions (organized by data type)
# ============================================================================


def calculate_average_rating(rating_data: Optional[Dict[str, Any]]) -> float:
    """
    Calculate average rating excluding review count.

    Args:
        rating_data: Dictionary containing rating information

    Returns:
        Average rating as a float, rounded to 2 decimal places
    """
    if not rating_data:
        logger.warning("Rating data is empty or None")
        return 0.0

    # Extract numeric ratings, excluding review_count
    ratings: List[float] = []
    for key, value in rating_data.items():
        if key == "review_count":
            continue

        try:
            # Handle string values that might contain numeric ratings
            if isinstance(value, str) and value.strip():
                rating_value = float(value)
            elif isinstance(value, (int, float)):
                rating_value = float(value)
            else:
                continue

            # Validate rating is in reasonable range (0-5 or 0-10)
            if 0 <= rating_value <= 10:
                ratings.append(rating_value)

        except (ValueError, TypeError):
            logger.debug(f"Skipping non-numeric rating value: {key}={value}")
            continue

    if not ratings:
        logger.warning("No valid ratings found in rating data")
        return 0.0

    return round(sum(ratings) / len(ratings), 2)


def extract_price(data: Dict[str, Any]) -> float:
    """
    Extract price from listing data.

    Args:
        data: Dictionary containing listing data with price information

    Returns:
        Price as a float, using discounted price if available, otherwise regular price
    """
    try:
        price_data = data.get("price", {})
        main_price_data = price_data.get("main", {})

        # Try discounted price first, then regular price
        discounted_price = main_price_data.get("discountedPrice", "")
        regular_price = main_price_data.get("price", "")

        # Handle case where prices might be empty dicts or other types
        if not isinstance(discounted_price, (str, int, float)):
            discounted_price = ""
        if not isinstance(regular_price, (str, int, float)):
            regular_price = ""

        discounted_price_value = _extract_numeric_price(discounted_price)
        regular_price_value = _extract_numeric_price(regular_price)

        # Return discounted price if available, otherwise regular price
        final_price = (
            discounted_price_value
            if discounted_price_value > 0
            else regular_price_value
        )

        if final_price == 0:
            logger.warning("No valid price found in listing data")

        return final_price

    except Exception as e:
        logger.warning(f"Error extracting price data: {e}")
        return 0.0


def extract_amenities(amenities_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Extract and organize amenities data.

    Args:
        amenities_data: List of amenity dictionaries

    Returns:
        Dictionary with amenity categories as keys and lists of amenities as values
    """
    if not amenities_data:
        return {}

    amenities: Dict[str, List[str]] = {}

    for entry in amenities_data:
        if not entry or "title" not in entry or "values" not in entry:
            logger.warning(f"Skipping malformed amenity entry: {entry}")
            continue

        amenity_title = str(entry["title"]).strip()
        if not amenity_title:
            continue

        try:
            values: List[Dict[str, str | bool]] = entry["values"]

            amenity_values: List[str] = []
            for item in values:
                if "title" in item:
                    result = str(item["title"]).strip()

                    if "subtitle" in item:
                        result += f": ({str(item['subtitle']).strip()})"

                    if result:
                        amenity_values.append(result)

            if amenity_values:
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

    if not location_descriptions:
        return location, getting_around

    for description in location_descriptions:
        if (
            not description
            or "title" not in description
            or "content" not in description
        ):
            logger.warning(f"Skipping malformed location description: {description}")
            continue

        title = str(description["title"]).lower().strip()
        content = _clean_html_content(str(description["content"]))

        if title == "getting around":
            getting_around = content
        elif title == "neighbourhood highlights":
            location = content
        elif not location and content:
            # Use the first description as location if not specifically categorized
            location = content

    return location, getting_around


def extract_highlights(highlights_data: List[Dict[str, Any]]) -> List[str]:
    """
    Extract listing highlights/features.

    Args:
        highlights_data: List of highlight dictionaries

    Returns:
        List of highlight titles
    """
    if not highlights_data:
        return []

    highlights: List[str] = []

    for highlight in highlights_data:
        if highlight and "title" in highlight:
            title = str(highlight["title"]).strip()
            if title:
                highlights.append(title)

    return highlights


def extract_reviews_summary(
    reviews_data: List[Dict[str, Any]],
) -> List[Dict[str, str | int]]:
    """
    Extract review summary statistics.

    Args:
        reviews_data: List of review dictionaries

    Returns:
        Dictionary containing review summary statistics
    """
    if not reviews_data:
        return []

    recent_reviews: List[Dict[str, str | int]] = []

    for review in reviews_data:
        if not review:
            continue

        # Check for required fields and English language only
        if (
            "comments" in review
            and "rating" in review
            and review.get("language", "").lower() == "en"
            and len(recent_reviews) < 5
        ):
            comment = str(review["comments"]).strip()
            if comment:  # Only add non-empty comments
                try:
                    rating = int(review["rating"])
                    recent_reviews.append(
                        {
                            "comment": comment,
                            "rating": rating,
                            "date": str(review.get("localizedDate", "")).strip(),
                        }
                    )
                except (ValueError, TypeError):
                    logger.debug(
                        f"Skipping review with invalid rating: {review.get('rating')}"
                    )

    return recent_reviews


def extract_house_rules(house_rules_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract house rules information.

    Args:
        house_rules_data: Dictionary containing house rules

    Returns:
        Dictionary with organized house rules
    """
    if not house_rules_data:
        return {
            "additional_rules": [],
            "general_rules": [],
            "check_in_out": [],
        }

    # Handle additional rules as a list
    additional_rules_raw = house_rules_data.get("additional", "")
    additional_rules = []
    if additional_rules_raw:
        # Convert to string and split by newlines
        raw_string = str(additional_rules_raw)
        # Split by newlines and filter out empty strings
        rules_list = [rule.strip() for rule in raw_string.split("\n") if rule.strip()]
        if rules_list:
            additional_rules = rules_list
        else:
            # If no newlines, treat as single rule (only if not empty)
            clean_rule = raw_string.strip()
            if clean_rule:
                additional_rules = [clean_rule]

    rules: Dict[str, Any] = {
        "additional_rules": additional_rules,
        "general_rules": [],
        "check_in_out": [],
    }

    # General rules
    general_rules = house_rules_data.get("general", [])
    if not isinstance(general_rules, list):
        return rules

    for rule_group in general_rules:
        if not rule_group or not isinstance(rule_group, dict):
            continue

        if "title" not in rule_group or "values" not in rule_group:
            continue

        title = str(rule_group["title"]).strip()
        values = rule_group["values"]

        if not isinstance(values, list):
            continue

        rule_values: List[str] = []
        for item in values:
            if item and isinstance(item, dict) and "title" in item:
                item_title = str(item["title"]).strip()
                if item_title:
                    rule_values.append(item_title)

        if rule_values:
            if title.lower() == "checking in and out":
                rules["check_in_out"] = rule_values
            else:
                rules["general_rules"].append({"category": title, "rules": rule_values})

    return rules


def extract_property_details(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract detailed property information.

    Args:
        data: Raw scraped data

    Returns:
        Dictionary containing property details
    """
    # Get layout information safely
    layout_items = []
    sub_description = data.get("sub_description", {})
    if isinstance(sub_description, dict):
        layout_items = sub_description.get("items", [])
        if not isinstance(layout_items, list):
            layout_items = []

    return {
        "room_type": str(data.get("room_type", "")).strip(),
        "is_guest_favorite": bool(data.get("is_guest_favorite", False)),
        "is_super_host": bool(data.get("is_super_host", False)),
        "layout": layout_items,
    }


# ============================================================================
# File I/O Functions
# ============================================================================


def _write_debug_json(data: Dict[str, Any], listing_id: int) -> None:
    """
    Write raw data to JSON file for debugging/backup.

    Args:
        data: Raw data to write
        listing_id: Listing identifier for filename
    """
    try:
        # Use /tmp directory or fallback to current directory
        tmp_dir = Path("/tmp")
        if not tmp_dir.exists() or not tmp_dir.is_dir():
            tmp_dir = Path(".")

        json_filepath = tmp_dir / f"listing_{listing_id}.json"

        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Raw data written to {json_filepath}")

    except (IOError, TypeError, OSError) as e:
        logger.warning(f"Failed to write JSON file for listing {listing_id}: {e}")


# ============================================================================
# Main Processing Functions
# ============================================================================


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
        ValueError: If required data is missing or invalid
        KeyError: If required fields are missing from data
    """
    if not data:
        raise ValueError("Data must be a non-empty dictionary")

    if listing_id <= 0:
        raise ValueError("Listing ID must be a positive integer")

    if not link.strip():
        raise ValueError("Link must be a non-empty string")

    if stay_length <= 0:
        raise ValueError("Stay length must be a positive integer")

    # Write debug JSON file
    _write_debug_json(data, listing_id)

    try:
        # Extract basic information first
        total_cost = extract_price(data)

        info: Dict[str, Any] = {
            "id": listing_id,
            "url": link.strip(),
            "duration": stay_length,
            "cost": total_cost,
        }

        # Extract coordinates safely
        coordinates = data.get("coordinates", {})
        if isinstance(coordinates, dict):
            info["coordinates"] = json.dumps(coordinates)
        else:
            logger.warning("Invalid coordinates data")
            info["coordinates"] = json.dumps({})

        # Extract basic property information
        info["super_host"] = bool(data.get("is_super_host", False))
        info["capacity"] = int(data.get("person_capacity", 0))

        # Calculate average rating with error handling
        rating_data = data.get("rating", {})
        info["average_rating"] = calculate_average_rating(rating_data)

        # Extract check-in/out information from house rules
        house_rules = data.get("house_rules", {})
        extracted_rules = extract_house_rules(house_rules)
        info["check_in_out"] = extracted_rules.get("check_in_out", [])

        # Extract other information
        info["amenities"] = extract_amenities(data.get("amenities", []))

        # Extract images safely
        images_data = data.get("images", [])
        info["images"] = []
        if isinstance(images_data, list):
            for img in images_data:
                if img and isinstance(img, dict) and "url" in img:
                    url = str(img["url"]).strip()
                    if url:
                        info["images"].append(url)

        # Location information
        location_descriptions = data.get("location_descriptions", [])
        location, getting_around = extract_location_info(location_descriptions)
        info["location"] = location
        info["getting_around"] = getting_around

        # Additional extracted information
        info["highlights"] = extract_highlights(data.get("highlights", []))
        info["reviews_summary"] = extract_reviews_summary(data.get("reviews", []))
        info["house_rules"] = extracted_rules
        info["property_details"] = extract_property_details(data)

        return info

    except KeyError as e:
        logger.error(f"Missing required field in scraped data: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing listing data for ID {listing_id}: {e}")
        raise


def validate_listing_data(listing_data: Dict[str, Any]) -> bool:
    """
    Validate that listing data contains required fields.

    Args:
        listing_data: Dictionary containing listing information

    Returns:
        True if valid, False otherwise
    """
    if not listing_data:
        logger.error("Listing data must be a non-empty dictionary")
        return False

    missing_fields: List[str] = []
    for field in REQUIRED_LISTING_FIELDS:
        if field not in listing_data:
            missing_fields.append(field)

    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        return False

    # Additional validation for specific fields
    listing_id = listing_data.get("id")
    if not isinstance(listing_id, int) or listing_id <= 0:
        logger.error("ID must be a positive integer")
        return False

    url = listing_data.get("url")
    if not isinstance(url, str) or not url.strip():
        logger.error("URL must be a non-empty string")
        return False

    cost = listing_data.get("cost")
    if not isinstance(cost, (int, float)) or cost < 0:
        logger.error("Cost must be a non-negative number")
        return False

    return True
