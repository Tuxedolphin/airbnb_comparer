"""
Logging configuration for the Airbnb listing scraper application.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        include_timestamp: Whether to include timestamp in logs

    Returns:
        Configured logger instance
    """
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


# Create a default logger for the application
logger = setup_logging()
