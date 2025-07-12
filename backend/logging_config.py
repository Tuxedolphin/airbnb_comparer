"""
Logging configuration for the Airbnb listing scraper application.

Enhanced logging format includes:
- Logger name (module name)
- Log level
- Filename and line number
- Function name
- Log message

This provides comprehensive tracking information for debugging and monitoring
without timestamp clutter.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = False,
) -> logging.Logger:
    """
    Set up enhanced logging configuration for the application.

    The default format includes filename, line number, and function name
    for comprehensive tracking and debugging.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        include_timestamp: Whether to include timestamp in logs (default: False)

    Returns:
        Configured logger instance with enhanced tracking information
    """
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s"

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
