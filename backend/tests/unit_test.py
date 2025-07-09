"""
Unit tests for the refactored Airbnb listing scraper modules.
"""

import json
import pytest
import tempfile
import os
import logging
import sys
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from typing import Dict, Any, List

# Import modules to test
from backend.constants import CHECKBOX_FIELD_MAPPING, DATABASE_PATH
from backend.url_utils import extract_from_url, validate_airbnb_url
from backend.data_processor import (
    calculate_average_rating,
    extract_amenities,
    extract_location_info,
    process_listing_data,
    validate_listing_data,
)
from backend.data_retrieval import (
    extract_field_from_listing,
    get_available_fields,
)
from backend.db_helpers import DatabaseManager
from backend.validation import (
    validate_url_format,
    validate_listing_id,
    validate_required_fields,
    validate_database_path,
    sanitize_string,
    validate_json_data,
)
from backend.scraper import (
    scrape_listing_data,
    add_listing,
    update_listing_costs,
)
from backend.logging_config import setup_logging
from backend.main import main


class TestUrlUtils:
    """Test cases for URL processing utilities."""

    def test_extract_from_url_valid(self):
        """Test extraction from valid Airbnb URL."""
        url = "https://www.airbnb.com/rooms/12345?check_in=2023-12-01&check_out=2023-12-05&adults=2"

        listing_id, duration, check_in, check_out, adults = extract_from_url(url)

        assert listing_id == 12345
        assert duration == 4
        assert check_in == "2023-12-01"
        assert check_out == "2023-12-05"
        assert adults == 2

    def test_extract_from_url_invalid_format(self):
        """Test extraction from invalid URL format."""
        url = "https://example.com/invalid"

        with pytest.raises(ValueError, match="Invalid Airbnb URL format"):
            extract_from_url(url)

    def test_extract_from_url_invalid_dates(self):
        """Test extraction with invalid date order."""
        url = "https://www.airbnb.com/rooms/12345?check_in=2023-12-05&check_out=2023-12-01&adults=2"

        with pytest.raises(
            ValueError, match="Check-out date must be after check-in date"
        ):
            extract_from_url(url)

    def test_validate_airbnb_url_valid(self):
        """Test URL validation with valid URL."""
        url = "https://www.airbnb.com/rooms/12345?check_in=2023-12-01&check_out=2023-12-05&adults=2"

        assert validate_airbnb_url(url) is True

    def test_validate_airbnb_url_invalid(self):
        """Test URL validation with invalid URL."""
        url = "https://example.com/invalid"

        assert validate_airbnb_url(url) is False


class TestDataProcessor:
    """Test cases for data processing utilities."""

    def test_calculate_average_rating(self):
        """Test rating calculation."""
        rating_data: Dict[str, Any] = {
            "cleanliness": 4.5,
            "communication": 4.8,
            "location": 4.2,
            "review_count": 150,  # Should be excluded
        }

        result = calculate_average_rating(rating_data)
        expected = round((4.5 + 4.8 + 4.2) / 3, 2)

        assert result == expected

    def test_calculate_average_rating_empty(self):
        """Test rating calculation with empty data."""
        rating_data: Dict[str, Any] = {"review_count": 150}

        result = calculate_average_rating(rating_data)

        assert result == 0.0

    def test_extract_amenities(self):
        """Test amenities extraction."""
        amenities_data: List[Dict[str, Any]] = [
            {
                "title": "Kitchen",
                "values": [
                    {"title": "Refrigerator"},
                    {"title": "Microwave"},
                ],
            },
            {
                "title": "Bathroom",
                "values": [
                    {"title": "Hair dryer"},
                    {"title": "Shampoo"},
                ],
            },
        ]

        result = extract_amenities(amenities_data)

        expected = {
            "Kitchen": ["Refrigerator", "Microwave"],
            "Bathroom": ["Hair dryer", "Shampoo"],
        }

        assert result == expected

    def test_extract_location_info(self):
        """Test location information extraction."""
        location_descriptions = [
            {"title": "Downtown Tokyo", "content": "Great location"},
            {
                "title": "Getting Around",
                "content": "Take the metro<br />Walk 5 minutes",
            },
        ]

        location, getting_around = extract_location_info(location_descriptions)

        assert location == "Downtown Tokyo"
        assert getting_around == "Take the metro\nWalk 5 minutes"

    def test_extract_location_info_invalid_count(self):
        """Test location extraction with wrong number of descriptions."""
        location_descriptions = [
            {"title": "Downtown Tokyo", "content": "Great location"}
        ]

        with pytest.raises(ValueError, match="Expected 2 location descriptions"):
            extract_location_info(location_descriptions)

    def test_validate_listing_data_valid(self):
        """Test listing data validation with valid data."""
        listing_data: Dict[str, Any] = {
            "id": 12345,
            "url": "https://airbnb.com/rooms/12345",
            "duration": 4,
            "daily_cost": 100,
            "misc_cost": 50,
        }

        assert validate_listing_data(listing_data) is True

    def test_validate_listing_data_invalid(self):
        """Test listing data validation with missing fields."""
        listing_data: Dict[str, Any] = {
            "id": 12345,
            "url": "https://airbnb.com/rooms/12345",
            # Missing duration, daily_cost, misc_cost
        }

        assert validate_listing_data(listing_data) is False


class TestDataRetrieval:
    """Test cases for data retrieval utilities."""

    def test_extract_field_from_listing_basic(self):
        """Test basic field extraction."""
        listing: Dict[str, Any] = {
            "id": 12345,
            "location": "Tokyo",
            "duration": 4,
            "daily_cost": 100,
            "misc_cost": 50,
            "images": ["image1.jpg", "image2.jpg"],
        }

        assert extract_field_from_listing("ID", listing) == 12345
        assert extract_field_from_listing("Location", listing) == "Tokyo"

    def test_extract_field_from_listing_calculated_cost(self):
        """Test calculated cost field extraction."""
        listing: Dict[str, Any] = {
            "duration": 4,
            "daily_cost": 100,
            "misc_cost": 50,
        }

        result = extract_field_from_listing("Cost", listing)
        expected = 100 * 4 + 50  # 450

        assert result == expected

    def test_extract_field_from_listing_cover_image(self):
        """Test cover image extraction."""
        listing: Dict[str, Any] = {
            "images": ["image1.jpg", "image2.jpg"],
        }

        result = extract_field_from_listing("Cover", listing)

        assert result == "image1.jpg"

    def test_extract_field_from_listing_unknown_field(self):
        """Test extraction with unknown field."""
        listing: Dict[str, Any] = {"id": 12345}

        with pytest.raises(KeyError, match="Unknown field"):
            extract_field_from_listing("UnknownField", listing)

    def test_get_available_fields(self):
        """Test getting available fields."""
        fields = get_available_fields()

        assert isinstance(fields, list)
        assert "ID" in fields
        assert "Location" in fields
        assert "Cost" in fields


class TestDatabaseManager:
    """Test cases for database operations."""

    def test_database_manager_context(self):
        """Test DatabaseManager context manager."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Test adding and retrieving a listing
                listing_data: Dict[str, Any] = {
                    "id": 12345,
                    "url": "https://airbnb.com/rooms/12345",
                    "duration": 4,
                    "daily_cost": 100,
                    "misc_cost": 50,
                }

                db_manager.add_entry(listing_data)
                retrieved = db_manager.get_listing(12345)

                assert retrieved is not None
                assert retrieved["id"] == 12345
                assert retrieved["url"] == "https://airbnb.com/rooms/12345"

        finally:
            os.unlink(db_path)

    def test_database_manager_listing_exists(self):
        """Test listing existence check."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Initially should not exist
                assert db_manager.listing_exists(12345) is False

                # Add a listing
                listing_data: Dict[str, Any] = {
                    "id": 12345,
                    "url": "https://airbnb.com/rooms/12345",
                    "duration": 4,
                    "daily_cost": 100,
                    "misc_cost": 50,
                }

                db_manager.add_entry(listing_data)

                # Now should exist
                assert db_manager.listing_exists(12345) is True

        finally:
            os.unlink(db_path)


class TestValidation:
    """Test cases for validation utilities."""

    def test_validate_url_format_valid_http(self):
        """Test URL format validation with valid HTTP URL."""
        assert validate_url_format("http://example.com") is True

    def test_validate_url_format_valid_https(self):
        """Test URL format validation with valid HTTPS URL."""
        assert validate_url_format("https://example.com") is True

    def test_validate_url_format_invalid_empty(self):
        """Test URL format validation with empty string."""
        assert validate_url_format("") is False

    def test_validate_url_format_invalid_whitespace(self):
        """Test URL format validation with whitespace."""
        assert validate_url_format("   ") is False

    def test_validate_url_format_invalid_no_protocol(self):
        """Test URL format validation without protocol."""
        assert validate_url_format("example.com") is False

    def test_validate_listing_id_valid(self):
        """Test listing ID validation with valid integer."""
        assert validate_listing_id(12345) is True

    def test_validate_listing_id_invalid_zero(self):
        """Test listing ID validation with zero."""
        assert validate_listing_id(0) is False

    def test_validate_listing_id_invalid_negative(self):
        """Test listing ID validation with negative number."""
        assert validate_listing_id(-1) is False

    def test_validate_listing_id_invalid_string(self):
        """Test listing ID validation with string."""
        assert validate_listing_id("12345") is False

    def test_validate_listing_id_invalid_float(self):
        """Test listing ID validation with float."""
        assert validate_listing_id(123.45) is False

    def test_validate_listing_id_invalid_none(self):
        """Test listing ID validation with None."""
        assert validate_listing_id(None) is False

    def test_validate_required_fields_all_present(self):
        """Test required fields validation with all fields present."""
        data: Dict[str, Any] = {"id": 1, "name": "test", "url": "https://example.com"}
        required = ["id", "name", "url"]

        result = validate_required_fields(data, required)
        assert result == []

    def test_validate_required_fields_missing_some(self):
        """Test required fields validation with missing fields."""
        data: Dict[str, Any] = {"id": 1, "name": "test"}
        required = ["id", "name", "url", "duration"]

        result = validate_required_fields(data, required)
        assert result == ["url", "duration"]

    def test_validate_required_fields_empty_data(self):
        """Test required fields validation with empty data."""
        data: Dict[str, Any] = {}
        required = ["id", "name"]

        result = validate_required_fields(data, required)
        assert result == ["id", "name"]

    def test_validate_database_path_valid(self):
        """Test database path validation with valid path."""
        assert validate_database_path("/path/to/database.db") is True

    def test_validate_database_path_invalid_empty(self):
        """Test database path validation with empty path."""
        assert validate_database_path("") is False

    def test_validate_database_path_invalid_none(self):
        """Test database path validation with None."""
        assert validate_database_path(None) is False

    def test_validate_database_path_invalid_no_extension(self):
        """Test database path validation without .db extension."""
        assert validate_database_path("/path/to/database") is False

    def test_validate_database_path_invalid_wrong_extension(self):
        """Test database path validation with wrong extension."""
        assert validate_database_path("/path/to/database.txt") is False

    def test_validate_database_path_invalid_short(self):
        """Test database path validation with too short path."""
        assert validate_database_path(".db") is False

    def test_sanitize_string_normal(self):
        """Test string sanitization with normal string."""
        result = sanitize_string("  Hello World  ")
        assert result == "Hello World"

    def test_sanitize_string_none(self):
        """Test string sanitization with None."""
        result = sanitize_string(None)
        assert result == ""

    def test_sanitize_string_number(self):
        """Test string sanitization with number."""
        result = sanitize_string(12345)
        assert result == "12345"

    def test_sanitize_string_max_length(self):
        """Test string sanitization with length limit."""
        long_string = "a" * 1500
        result = sanitize_string(long_string, max_length=1000)
        assert len(result) == 1000
        assert result == "a" * 1000

    @patch("backend.validation.logger")
    def test_sanitize_string_truncation_warning(self, mock_logger: MagicMock):
        """Test string sanitization logs warning when truncating."""
        long_string = "a" * 1500
        sanitize_string(long_string, max_length=1000)
        mock_logger.warning.assert_called_once()

    def test_validate_json_data_valid(self):
        """Test JSON validation with valid data."""
        data: Dict[str, Any] = {"key": "value", "number": 123, "list": [1, 2, 3]}
        assert validate_json_data(data) is True

    def test_validate_json_data_invalid_function(self):
        """Test JSON validation with function (non-serializable)."""
        data: Dict[str, Any] = {"key": lambda x: x}  # type: ignore
        assert validate_json_data(data) is False

    def test_validate_json_data_invalid_complex_object(self):
        """Test JSON validation with complex object."""
        data: Dict[str, Any] = {"key": object()}
        assert validate_json_data(data) is False


class TestScraper:
    """Test cases for scraping utilities."""

    @patch("backend.scraper.pyairbnb.get_details")
    @patch("builtins.open", new_callable=MagicMock)
    def test_scrape_listing_data_success(self, mock_open: MagicMock, mock_get_details: MagicMock):
        """Test successful listing data scraping."""
        mock_data: Dict[str, Any] = {
            "id": 12345,
            "name": "Test Listing",
            "location": "Test Location",
        }
        mock_get_details.return_value = mock_data

        result = scrape_listing_data(
            "https://airbnb.com/rooms/12345",
            "2023-12-01",
            "2023-12-05",
            2,
            "USD",
        )

        assert result == mock_data
        mock_get_details.assert_called_once_with(
            room_url="https://airbnb.com/rooms/12345",
            currency="USD",
            check_in="2023-12-01",
            check_out="2023-12-05",
            adults=2,
        )

    @patch("backend.scraper.pyairbnb.get_details")
    def test_scrape_listing_data_failure(self, mock_get_details: MagicMock):
        """Test scraping failure handling."""
        mock_get_details.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="Failed to scrape listing data"):
            scrape_listing_data(
                "https://airbnb.com/rooms/12345",
                "2023-12-01",
                "2023-12-05",
                2,
            )

    @patch("backend.scraper.scrape_listing_data")
    @patch("backend.scraper.extract_from_url")
    @patch("backend.scraper.process_listing_data")
    @patch("backend.scraper.validate_listing_data")
    @patch("backend.scraper.DatabaseManager")
    def test_add_listing_success(
        self, mock_db_manager: MagicMock, mock_validate: MagicMock, mock_process: MagicMock, mock_extract: MagicMock, mock_scrape: MagicMock
    ):
        """Test successful listing addition."""
        # Setup mocks
        mock_extract.return_value = (12345, 4, "2023-12-01", "2023-12-05", 2)
        mock_scrape.return_value = {"raw": "data"}
        mock_process.return_value = {
            "id": 12345,
            "url": "test",
            "duration": 4,
            "daily_cost": 100,
            "misc_cost": 50,
        }
        mock_validate.return_value = True

        mock_db_instance = MagicMock()
        mock_db_manager.return_value.__enter__.return_value = mock_db_instance

        # Execute
        add_listing("https://airbnb.com/rooms/12345", 450)

        # Verify
        mock_extract.assert_called_once()
        mock_scrape.assert_called_once()
        mock_process.assert_called_once()
        mock_validate.assert_called_once()
        mock_db_instance.create_tables.assert_called_once()
        mock_db_instance.add_entry.assert_called_once()

    @patch("backend.scraper.extract_from_url")
    @patch("backend.scraper.validate_listing_data")
    def test_add_listing_invalid_data(self, mock_validate: MagicMock, mock_extract: MagicMock):
        """Test listing addition with invalid data."""
        mock_extract.return_value = (12345, 4, "2023-12-01", "2023-12-05", 2)
        mock_validate.return_value = False

        with pytest.raises(ValueError, match="Processed listing data is invalid"):
            with patch("backend.scraper.scrape_listing_data"), patch(
                "backend.scraper.process_listing_data"
            ):
                add_listing("https://airbnb.com/rooms/12345", 450)

    @patch("backend.scraper.DatabaseManager")
    def test_update_listing_costs_success(self, mock_db_manager: MagicMock):
        """Test successful listing cost update."""
        mock_db_instance = MagicMock()
        mock_db_manager.return_value.__enter__.return_value = mock_db_instance

        mock_listing_data: Dict[str, Any] = {
            "id": 12345,
            "url": "https://airbnb.com/rooms/12345",
            "duration": 4,
            "daily_cost": 100,
            "misc_cost": 50,
        }
        mock_db_instance.get_listing.return_value = mock_listing_data

        result = update_listing_costs(12345, 120)

        assert result is True
        mock_db_instance.get_listing.assert_called_once_with(12345)
        mock_db_instance.add_entry.assert_called_once()

    @patch("backend.scraper.DatabaseManager")
    def test_update_listing_costs_not_found(self, mock_db_manager: MagicMock):
        """Test listing cost update when listing not found."""
        mock_db_instance = MagicMock()
        mock_db_manager.return_value.__enter__.return_value = mock_db_instance
        mock_db_instance.get_listing.return_value = None

        result = update_listing_costs(12345, 120)

        assert result is False

    @patch("backend.scraper.DatabaseManager")
    def test_update_listing_costs_database_error(self, mock_db_manager: MagicMock):
        """Test listing cost update with database error."""
        mock_db_manager.side_effect = Exception("Database error")

        result = update_listing_costs(12345, 120)

        assert result is False


class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        logger = setup_logging()

        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        logger = setup_logging(level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_logging_custom_format(self):
        """Test logging setup with custom format."""
        custom_format = "%(levelname)s - %(message)s"
        logger = setup_logging(format_string=custom_format)

        assert isinstance(logger, logging.Logger)

    def test_setup_logging_no_timestamp(self):
        """Test logging setup without timestamp."""
        logger = setup_logging(include_timestamp=False)

        assert isinstance(logger, logging.Logger)


class TestMain:
    """Test cases for main entry point."""

    @patch("backend.main.DatabaseManager")
    @patch("backend.main.setup_logging")
    @patch("backend.main.get_available_fields")
    def test_main_success(
        self, mock_get_fields: MagicMock, mock_setup_logging: MagicMock, mock_db_manager: MagicMock
    ):
        """Test successful main function execution."""
        mock_get_fields.return_value = ["ID", "Location", "Cost"]
        mock_db_instance = MagicMock()
        mock_db_instance.get_listing_count.return_value = 5
        mock_db_manager.return_value.__enter__.return_value = mock_db_instance

        main()

        mock_setup_logging.assert_called_once()
        mock_get_fields.assert_called_once()
        mock_db_instance.create_tables.assert_called_once()
        mock_db_instance.get_listing_count.assert_called_once()

    @patch("backend.main.DatabaseManager")
    @patch("backend.main.setup_logging")
    @patch("backend.main.get_available_fields")
    def test_main_database_error(
        self, mock_get_fields: MagicMock, mock_setup_logging: MagicMock, mock_db_manager: MagicMock
    ):
        """Test main function with database error."""
        mock_get_fields.return_value = ["ID", "Location", "Cost"]
        mock_db_manager.side_effect = Exception("Database connection failed")

        # Should not raise exception, just log error
        main()

        mock_setup_logging.assert_called_once()
        mock_get_fields.assert_called_once()


class TestDatabaseManagerAdditional:
    """Additional test cases for DatabaseManager methods."""

    def test_database_manager_get_all_listings(self):
        """Test retrieving all listings from database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Add multiple listings
                listing1: Dict[str, Any] = {
                    "id": 1,
                    "url": "https://airbnb.com/rooms/1",
                    "duration": 3,
                    "daily_cost": 100,
                    "misc_cost": 30,
                }
                listing2: Dict[str, Any] = {
                    "id": 2,
                    "url": "https://airbnb.com/rooms/2",
                    "duration": 5,
                    "daily_cost": 150,
                    "misc_cost": 50,
                }

                db_manager.add_entry(listing1)
                db_manager.add_entry(listing2)

                # Retrieve all listings
                all_listings = db_manager.get_all_listings()

                assert len(all_listings) == 2
                assert any(listing["id"] == 1 for listing in all_listings)
                assert any(listing["id"] == 2 for listing in all_listings)

        finally:
            os.unlink(db_path)

    def test_database_manager_get_listing_count(self):
        """Test getting listing count from database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Initially should be 0
                assert db_manager.get_listing_count() == 0

                # Add a listing
                listing_data: Dict[str, Any] = {
                    "id": 12345,
                    "url": "https://airbnb.com/rooms/12345",
                    "duration": 4,
                    "daily_cost": 100,
                    "misc_cost": 50,
                }

                db_manager.add_entry(listing_data)

                # Should be 1
                assert db_manager.get_listing_count() == 1

        finally:
            os.unlink(db_path)

    def test_database_manager_delete_listing(self):
        """Test deleting a listing from database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Add a listing
                listing_data: Dict[str, Any] = {
                    "id": 12345,
                    "url": "https://airbnb.com/rooms/12345",
                    "duration": 4,
                    "daily_cost": 100,
                    "misc_cost": 50,
                }

                db_manager.add_entry(listing_data)

                # Verify it exists
                assert db_manager.listing_exists(12345) is True

                # Delete it
                result = db_manager.delete_listing(12345)
                assert result is True

                # Verify it's gone
                assert db_manager.listing_exists(12345) is False

        finally:
            os.unlink(db_path)

    def test_database_manager_delete_listing_not_found(self):
        """Test deleting a non-existent listing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Try to delete non-existent listing
                result = db_manager.delete_listing(99999)
                assert result is False

        finally:
            os.unlink(db_path)

    def test_database_manager_get_listing_not_found(self):
        """Test retrieving a non-existent listing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Try to get non-existent listing
                result = db_manager.get_listing(99999)
                assert result is None

        finally:
            os.unlink(db_path)

    def test_database_manager_add_entry_missing_id(self):
        """Test adding entry without required ID field."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            with DatabaseManager(db_path) as db_manager:
                db_manager.create_tables()

                # Try to add entry without ID
                listing_data: Dict[str, Any] = {
                    "url": "https://airbnb.com/rooms/12345",
                    "duration": 4,
                    "daily_cost": 100,
                    "misc_cost": 50,
                }

                with pytest.raises(
                    ValueError, match="Listing data must contain 'id' field"
                ):
                    db_manager.add_entry(listing_data)

        finally:
            os.unlink(db_path)

    def test_database_manager_close_connection(self):
        """Test closing database connection."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            db_manager = DatabaseManager(db_path)
            db_manager.create_tables()  # This creates a connection

            # Close connection
            db_manager.close()

            # Connection should be None after closing
            assert db_manager._connection is None

        finally:
            os.unlink(db_path)

    def test_database_manager_connection_reuse(self):
        """Test that database connection is reused."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            db_manager = DatabaseManager(db_path)

            # Get connection twice
            conn1 = db_manager._get_connection()
            conn2 = db_manager._get_connection()

            # Should be the same connection object
            assert conn1 is conn2

            db_manager.close()

        finally:
            os.unlink(db_path)
