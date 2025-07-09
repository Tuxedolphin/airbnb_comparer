# Airbnb Listing Scraper and Database Manager - Refactored

This is a refactored version of the original Airbnb listing scraper that follows best practices for code organization and maintainability.

## Project Structure

The project has been refactored from a single `project.py` file into multiple focused modules:

```text
backend/
├── __init__.py              # Package interface - re-exports main functions
├── main.py                  # Main entry point script
├── constants.py             # Application constants
├── url_utils.py             # URL processing utilities
├── data_processor.py        # Data processing functions
├── data_retrieval.py        # Database retrieval functions
├── scraper.py               # Web scraping functions
├── db_helpers.py            # Database management
├── example_usage.py         # Usage examples
├── README.md                # Documentation
└── tests/                   # Unit tests
    └── test_refactored_modules.py
```

## Module Descriptions

### `constants.py`

- Application constants and configuration
- Field mappings for UI checkboxes
- Database paths and scraping defaults

### `url_utils.py`

- URL validation and parsing
- Extraction of listing details from Airbnb URLs
- Date validation and duration calculations

### `data_processor.py`

- Raw data processing and structuring
- Rating calculations
- Amenities extraction
- Location information processing

### `data_retrieval.py`

- Database query functions
- Field extraction utilities
- Search and filtering functions

### `scraper.py`

- Web scraping functionality
- Listing data retrieval from Airbnb
- Cost management and updates
- Integration with data processor

### `db_helpers.py`

- Database management using DatabaseManager class
- Connection handling
- Table creation and management
- CRUD operations

## Usage

### Running the Application

To run the main application:

```bash
# From the project root
python -m backend.main

# Or directly
python backend/main.py
```

### Importing Functions

You can import functions in two ways:

#### Option 1: From the package interface (recommended for most use cases)

```python
from backend import add_listing, get_listing_by_id, DatabaseManager
```

#### Option 2: Direct imports from specific modules (for advanced usage)

```python
from backend.scraper import add_listing
from backend.data_retrieval import get_listing_by_id
from backend.db_helpers import DatabaseManager
```

### Database Operations

The refactored code uses the `DatabaseManager` class:

```python
from backend.db_helpers import DatabaseManager
from backend.constants import DATABASE_PATH

with DatabaseManager(DATABASE_PATH) as db_manager:
    db_manager.create_tables()
    listing = db_manager.get_listing(12345)
```

## Key Improvements

1. **Modular Design**: Code is organized into focused modules with single responsibilities
2. **Better Error Handling**: Comprehensive error handling and validation
3. **Type Safety**: Proper type hints throughout the codebase
4. **Documentation**: Clear docstrings and inline comments
5. **Database Integration**: Uses the DatabaseManager class effectively
6. **Testing Ready**: Modular structure makes unit testing easier

## Usage Examples

### Adding a Listing

```python
from backend.scraper import add_listing

url = 'https://www.airbnb.com/rooms/12345?check_in=2023-12-01&check_out=2023-12-05&adults=2'
costs = [100, 50]  # [daily_cost, misc_cost]
add_listing(url, costs)
```

### Retrieving Data

```python
from backend.data_retrieval import get_listing_by_id, get_listings_by_location

# Get specific listing
listing = get_listing_by_id(12345)

# Search by location
tokyo_listings = get_listings_by_location("Tokyo")
```

## Error Handling

The refactored code includes comprehensive error handling:

- URL validation errors
- Database connection issues
- Data processing failures
- Scraping timeouts and failures

## Configuration

Configuration is centralized in `constants.py`:

- Database paths
- Field mappings
- Default values
- Debug settings

## Future Enhancements

The modular structure makes it easy to add:

- New data sources
- Additional validation rules
- Enhanced error reporting
- Performance optimizations
- Caching mechanisms
