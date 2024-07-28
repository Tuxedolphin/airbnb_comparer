import gobnb, json, sqlite3, re
from datetime import datetime


DATABASE = r"./db/database.db"


class Listing:

    @classmethod
    def add_listing(
        cls, link: str, costs: list, currency="SGD"
    ) -> None:
        """
        Scrapes the listing for the more important information, before storing it into a json file (more for myself)

        Results from scraping is in a dict that is then analysed, the rest of which is stored in a sqlite database
        """

        if not link or len(costs) != 2:
            raise ValueError("Invalid link or costs")

        # Calls another function to get the required information from the url
        id, stay_length = cls.extract_from_url(link)

        # Scrape the listing for the required information, except cost (AirBnB website is >:( )
        data = gobnb.Get_from_room_url(link, currency, "")

        # Format and export into json file for myself to see and debugging
        json_data = json.dumps(data, indent=4)
        with open("result.json", "w") as file:
            file.write(json_data)

        # Tidy and filter the more important information from the dictionary above
        info = {
            "id": id,
            "url": link,
            "duration": stay_length,
            "daily_cost": costs[0],
            "misc_cost": costs[1],
        }

        # Basic information
        info["coordinates"] = json.dumps(data["coordinates"])
        info["super_host"] = data["is_super_host"]
        info["capacity"] = data["person_capacity"]

        # Average rating
        info["average_rating"] = round(
            (
                sum(float(value) for key, value in data["rating"].items())
                - float(data["rating"]["review_count"])
            )
            / (len(data["rating"]) - 1),
            2,
        )

        # Check in and out
        info["check_in_out"] = [
            item["title"] for item in data["house_rules"]["general"][0]["values"]
        ]

        # Gets layout
        info["layout"] = [data["sub_description"]["items"]]

        # Gets amenities, creates an empty dictionary to store values in
        amenities = {}

        # Iterates over amenities, adding the title of each entry as the key and what it contains as the value
        for entry in data["amenities"]:
            amenity_title = entry["title"]
            amenity_values = [item["title"] for item in entry["values"]]

            amenities[amenity_title] = amenity_values

        info["amenities"] = amenities

        # Gets images into a list
        info["images"] = [dict_pair["url"] for dict_pair in data["images"]]

        # Gets location description
        if len(data["location_descriptions"]) != 2:
            return ValueError("length of location description is unexpected (not 2)")
        for dict_pair in data["location_descriptions"]:
            if dict_pair["title"].lower() == "getting around":
                info["getting_around"] = dict_pair["content"].replace("<br />", "\n")
            else:
                info["location"] = dict_pair["title"].replace("\u014d", "o")

        print("Scraping completed, all filtering of data done")
        print("Scraping completed, all filtering done")

        # Creates the tables to store the description if they do not yet exist
        create_tables(DATABASE)

        # Add the entry into SQLite
        sql_add_entry(DATABASE, info)

    @classmethod
    def extract_from_url(cls, link: str) -> None:
        """
        To extract information from the url provided, namely the id and duration of stay

        Args:
            link (str): Airbnb link
        """

        # Search through url for required information - id, check in and check out date
        match = re.search(
            r"^https:\/\/www\.airbnb\.com(?:\.sg)?\/rooms\/(\d+)\?.*check_in=(.{10}).*check_out=(.{10})",
            link,
        )

        # Identifying and storing of information from url
        id = match.group(1)
        check_in = datetime.fromisoformat(match.group(2))
        check_out = datetime.fromisoformat(match.group(3))

        if check_out < check_in:
            raise ValueError

        # Convert length of stay into number of days
        stay_length = check_out - check_in
        stay_length = int(stay_length.total_seconds() / (86_400))

        return id, stay_length

    @classmethod
    def sql_get(cls, id: int) -> dict:
        """
        Retrieves all the information of the particular listing from SQL and returns as a list

        Args:
            id (int): The particular ID of the listing

        Returns:
            dict: key value pairs of the required information
        """

        conn = sql_create_connection(DATABASE)

        with conn:
            cursor = conn.cursor()
            # Selects the json file
            cursor.execute("SELECT json FROM json WHERE listing_id = ?", (id,))

            # Fetches the json
            row = cursor.fetchone()

            # Select the others comments
            cursor.execute("SELECT notes FROM others WHERE listing_id = ?", (id,))
            notes = cursor.fetchone()

        if row:
            json_data = json.loads(row[0])
            json_data["notes"] = notes[0]
            return json_data
        else:
            print(f"Error: ID {id} not found")
            return None

    def __init__(self) -> None: ...

def retrieve_from_json(column: str, listing: dict) -> any:
    """
    Retrieves the required data from the given dictionary of listing

    Args:
        column (str): The column that the data belongs to
        listing (dict): The json/ dict of the listing

    Returns:
        any: returns the entry, which can be in any form such as a string or list
    """

    checkbox_contents = {
        "ID": "id",
        "Rating": "average_rating",
        "URL": "url",
        "Duration": "duration",
        "location": "location",
        "Getting Around": "getting_around",
        "Check In/ Out Timing": "check_in_out",
        "Layout": "layout",
        "Capacity": "capacity",
        "Cost": "cost",
        "Super Host": "super_host",
        "Amenities": "amenities",
        "Notes": "notes",
        "Images": "images",
        "Cover": "cover",
    }

    column = checkbox_contents[column]

    if column == "cost":
        # Calculate total cost
        return int(listing["daily_cost"]) * listing["duration"] + int(
            listing["misc_cost"]
        )

    elif column == "cover":
        # Get the cover photo
        return listing["images"][2]

    else:
        return listing[column]


def create_checkboxes() -> dict:
    """Sets up the checkboxes"""
    
    
    checkbox_contents = {
        "ID": "id",
        "Rating": "average_rating",
        "URL": "url",
        "Duration": "duration",
        "Coordinates": "coordinates",
        "Getting Around": "getting_around",
        "Check In/ Out Timing": "check_in_out",
        "Layout": "layout",
        "Capacity": "capacity",
        "Cost": "cost",
        "Super Host": "super_host",
        "Amenities": "amenities",
        "Notes": "notes",
        "Images": "images",
    }



def sql_create_connection(db_file: str) -> sqlite3.Connection:
    """
    Create a database connection to the sqlite database (db_file)

    Args:
        db_file (_type_): the file that the connection is made to
    """
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")

    return conn


def sql_create_table(conn: sqlite3.Connection, create_table_statement: str) -> None:
    """
    Creates a table from the 'table' statement

    Args:
        conn (_type_): The connection object
        table (_type_): the CREATE_TABLE statement
    """
    try:
        c = conn.cursor()
        c.execute(create_table_statement)
    except sqlite3.Error as e:
        print(f"SQLite error has occurred: {e}")


def create_tables(database: str) -> None:
    """
    Creates tables in SQLite, namely the main table, basic info table, and others table

    Args:
        database: the database that is going to be accessed
    """

    # Queries for creating the tables as required
    sql_create_main_table = """ CREATE TABLE IF NOT EXISTS main (
                                    id integer PRIMARY KEY,
                                    url text,
                                    duration integer
                                ); """

    sql_create_basic_info_table = """ CREATE TABLE IF NOT EXISTS basic_info (
                                        listing_id integer UNIQUE NOT NULL,
                                        coordinates,
                                        location,
                                        getting_around,
                                        check_in_out,
                                        layout,
                                        capacity,
                                        average_rating,
                                        daily_cost,
                                        misc_cost,
                                        super_host,
                                        FOREIGN KEY (listing_id) REFERENCES main (id)
                                    ); """

    sql_create_others_table = """ CREATE TABLE IF NOT EXISTS others (
                                        listing_id integer UNIQUE NOT NULL,
                                        amenities,
                                        images,
                                        notes,
                                        FOREIGN KEY (listing_id) REFERENCES main (id)
                                    ); """

    sql_create_json_table = """ CREATE TABLE IF NOT EXISTS json (
                                        listing_id integer UNIQUE NOT NULL,
                                        json,
                                        FOREIGN KEY (listing_id) REFERENCES main (id)
                                    ); """

    # Creates database connection
    conn = sql_create_connection(database)
    # Creates the tables
    if conn is not None:
        sql_create_table(conn, sql_create_main_table)
        sql_create_table(conn, sql_create_basic_info_table)
        sql_create_table(conn, sql_create_others_table)
        sql_create_table(conn, sql_create_json_table)
        print("All tables created")
    else:
        print("SQLite error: cannot create database connection.")


def sql_add_entry(database: str, items: dict) -> None:
    """
    Adds the entries into the database

    Args:
        database (str): The database for the items to be stored in
        items (dict): Keys are the columns while the values are the entry for each column
        status (customtkinter.Label): For the status
    """

    conn = sql_create_connection(database)

    with conn:

        cursor = conn.cursor()

        # Find the ID to start a new row in each table
        id = items["id"]

        # Ensure no duplicate
        try:
            cursor.execute("INSERT INTO main (id) VALUES (?)", (id,))
            cursor.execute("INSERT INTO basic_info (listing_id) VALUES (?)", (id,))
            cursor.execute("INSERT INTO others (listing_id) VALUES (?)", (id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite Error (Duplicate id): {e}")

        # Splits up each item in items into the column name and its value
        for column, value in items.items():
            # Check if it is ID
            if column == "id":
                continue

            table = db_table_filter(column)
            # If column not found
            if table == None:
                raise ValueError(f"Table not found for {column}: {value}")

            if table == "main":
                id_column_name = "id"
            else:
                id_column_name = "listing_id"

            # Sets up query to update the corresponding cell
            query = f"UPDATE {table} SET {column} = ? WHERE {id_column_name} = ?"

            # Sets values to json as there are lists and dicts
            cursor.execute(query, (json.dumps(value), id))

        # Stores the entire info dict as well to easily retrieve all values
        cursor.execute(
            "INSERT INTO json (listing_id, json) VALUES (?, ?)", (id, json.dumps(items))
        )

    conn.commit()
    print("Entry Submitted into Table")


def db_table_filter(column: str) -> str:
    """
    To find which table the column belongs in, and returns the table name

    Args:
        column (str): The column name
    """

    # Lists to hold which column belongs in which table
    main_table = ["id", "url", "duration"]
    basic_info_table = [
        "coordinates",
        "location",
        "super_host",
        "capacity",
        "check_in_out",
        "layout",
        "average_rating",
        "getting_around",
        "daily_cost",
        "misc_cost",
    ]
    others_table = ["amenities", "images", "notes"]
    id = ["id"]

    # Returns which table the column is found in
    column = column.lower()
    if column in main_table:
        return "main"
    if column in basic_info_table:
        return "basic_info"
    if column in others_table:
        return "others"
    if column in id:
        return "id"

    return None


def retrieve_from_location(location: str, database: str = DATABASE) -> list:
    """
    Retrieve all the listings that is located at a particular place

    Args:
        database (str): The database which contains the tables
        location (str): The location to search for

    Returns:
        list: Returns a list of dictionaries, each dictionary contains all the required information
        of a listing
    """

    conn = sql_create_connection(database)

    with conn:
        cursor = conn.cursor()

        # Search for all the rows which contains the location
        cursor.execute(
            f"SELECT listing_id FROM basic_info WHERE LOWER(location) LIKE LOWER(?)",
            (f"%{location}%",),
        )

        # Creates a list which stores all the IDs of the location
        ids = [int(row[0]) for row in cursor.fetchall()]
    
    # Creates a list of dicts to store the description of all the listings
    return [Listing.sql_get(id) for id in ids]


