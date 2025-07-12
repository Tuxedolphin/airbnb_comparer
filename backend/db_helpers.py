import sqlite3
import json
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, Generator, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEMA = {
    "main": """
        CREATE TABLE IF NOT EXISTS main (
            id INTEGER PRIMARY KEY,
            url TEXT,
            json TEXT NOT NULL
        )
    """
}


class DatabaseManager:
    """Database manager for handling SQLite operations with persistent connection."""

    def __init__(self, database_path: str):
        """
        Initialize the database manager.

        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
        self._connection: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get or create a persistent database connection.

        Returns:
            SQLite connection object

        Raises:
            sqlite3.Error: If connection fails
        """

        if self._connection is None:
            try:

                self._connection = sqlite3.connect(self.database_path)
                self._connection.row_factory = sqlite3.Row

                # Enable foreign key constraints
                self._connection.execute("PRAGMA foreign_keys = ON")

                # Enable WAL mode for better concurrency
                self._connection.execute("PRAGMA journal_mode = WAL")

                logger.debug(f"Created new database connection to {self.database_path}")

            except sqlite3.Error as e:
                logger.exception(f"Failed to create database connection: {e}")
                raise

        return self._connection

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections with transaction support.

        Yields:
            SQLite connection object

        Raises:
            sqlite3.Error: If connection fails
        """

        conn = self._get_connection()

        try:
            yield conn

        except sqlite3.Error as e:
            conn.rollback()
            logger.exception(f"Database operation failed, rolled back: {e}")
            raise

        except Exception as e:
            conn.rollback()
            logger.exception(f"Unexpected error, rolled back: {e}")
            raise

        else:
            conn.commit()

    def close(self) -> None:
        """Close the database connection."""

        if self._connection:
            self._connection.close()
            self._connection = None

            logger.debug("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Context manager exit."""

        if exc_type is not None:
            logger.exception(
                f"Exception occurred in DatabaseManager context: {exc_type.__name__}: {exc_val}"
            )

        self.close()

    def create_tables(self) -> None:
        """Create all required tables in the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for table_name, create_sql in SCHEMA.items():
                    cursor.execute(create_sql)
                    logger.debug(f"Created table: {table_name}")

                conn.commit()
                logger.info("Database tables created successfully")

        except sqlite3.Error as e:
            logger.exception(f"Error creating tables: {e}")
            raise

    def add_entry(self, listing_data: Dict[str, Any]) -> None:
        """
        Add a listing entry to the database.

        Args:
            listing_data: Dictionary containing listing information

        Raises:
            ValueError: If listing_data is missing required fields
            sqlite3.Error: If database operation fails
        """
        if "id" not in listing_data:
            raise ValueError("Listing data must contain 'id' field")

        listing_id = listing_data["id"]
        url = listing_data.get("url")
        json_data = json.dumps(listing_data)

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Insert or replace the entire record
                cursor.execute(
                    "INSERT OR REPLACE INTO main (id, url, json) VALUES (?, ?, ?)",
                    (listing_id, url, json_data),
                )

                logger.info(f"Successfully saved listing {listing_id} to database")

        except sqlite3.Error as e:
            logger.exception(f"Database error while adding entry {listing_id}: {e}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected error while adding entry {listing_id}: {e}")
            raise

    def get_listing(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a listing from the database.

        Args:
            listing_id: ID of the listing to retrieve

        Returns:
            Dictionary containing listing data or None if not found
        """
        try:
            with self.get_connection() as conn:

                cursor = conn.cursor()
                cursor.execute("SELECT json FROM main WHERE id = ?", (listing_id,))
                result = cursor.fetchone()

                if result:
                    return json.loads(result["json"])

                return None

        except sqlite3.Error as e:
            logger.exception(
                f"Database error while retrieving listing {listing_id}: {e}"
            )
            raise

        except json.JSONDecodeError as e:
            logger.exception(f"JSON decode error for listing {listing_id}: {e}")
            raise

    def get_all_listings(self) -> List[Dict[str, Any]]:
        """
        Retrieve all listings from the database.

        Returns:
            List of dictionaries containing listing data
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT json FROM main")
                results = cursor.fetchall()

                listings: List[Dict[str, Any]] = []

                for result in results:
                    try:
                        listing_data = json.loads(result["json"])
                        listings.append(listing_data)

                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON for a listing: {e}")
                        continue

                return listings

        except sqlite3.Error as e:
            logger.exception(f"Database error while retrieving all listings: {e}")
            raise

    def get_listing_count(self) -> int:
        """
        Get the total number of listings in the database.

        Returns:
            Total number of listings
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM main")

                result = cursor.fetchone()
                return result[0] if result else 0

        except sqlite3.Error as e:
            logger.exception(f"Database error while getting listing count: {e}")
            raise

    def delete_listing(self, listing_id: int) -> bool:
        """
        Delete a listing from the database.

        Args:
            listing_id: ID of the listing to delete

        Returns:
            True if listing was deleted, False if not found
        """
        try:
            with self.get_connection() as conn:

                cursor = conn.cursor()
                cursor.execute("DELETE FROM main WHERE id = ?", (listing_id,))
                deleted = cursor.rowcount > 0

                if deleted:
                    logger.info(f"Successfully deleted listing {listing_id}")

                else:
                    logger.warning(f"Listing {listing_id} not found for deletion")
                return deleted

        except sqlite3.Error as e:
            logger.exception(f"Database error while deleting listing {listing_id}: {e}")
            raise

    def listing_exists(self, listing_id: int) -> bool:
        """
        Check if a listing exists in the database.

        Args:
            listing_id: ID of the listing to check

        Returns:
            True if listing exists, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM main WHERE id = ? LIMIT 1", (listing_id,))
                return cursor.fetchone() is not None

        except sqlite3.Error as e:
            logger.exception(f"Database error while checking listing {listing_id}: {e}")
            raise
