import gobnb, json, tkinter, customtkinter, sqlite3, re
from datetime import datetime


class Listing:

    DATABASE = r"CS50x\db\database.db"

    @classmethod
    def add_listing(
        cls, link: str, costs: list, status: customtkinter.CTkLabel, currency="SGD"
    ) -> None:
        """
        Scrapes the listing for the more important information, before storing it into a json file (more for myself)

        Results from scraping is in a dict that is then analysed, the rest of which is stored in a sqlite database
        """

        # TODO Add changing status for customtkinter root

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
        info["average_rating"] = (
            sum(float(value) for key, value in data["rating"].items())
            - float(data["rating"]["review_count"])
        ) / (len(data["rating"]) - 1)

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
                info["location"] = dict_pair["title"]

        print("Scraping completed, all filtering of data done")
        status.configure(text="Scraping completed, all filtering done")

        # Creates the tables to store the description if they do not yet exist
        create_tables(cls.DATABASE)

        # Add the entry into SQLite
        sql_add_entry(cls.DATABASE, info, root)

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

        conn = sql_create_connection(cls.database)

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


def main():
    
    # Setting up the title page
    root = customtkinter.CTk()
    root_set_up(root)

    # Main loop for root to run
    root.mainloop()


def root_set_up(root: customtkinter.CTk) -> None:
    """Sets up the main page of the application"""

    # System Settings
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")

    # root Frame
    # Getting dimensions of screen
    width = 0.5 * root.winfo_screenwidth()
    height = 0.5 * root.winfo_screenheight()
    
    # Setting pop up to be full size              
    root.geometry("%dx%d" % (width, height))
    root.title("Airbnb")
    
    # Setting up UI for main page
    
    # Define a grid for the compare screen
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=8)
    root.rowconfigure(0, weight=12)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)
    
    # Place button in bottom left
    button_insert = customtkinter.CTkButton(root, text="Insert a Listing!", command=lambda: new_insert(root, status))
    button_insert.grid(row=1, column=0, sticky="s")
    
    # Status Label
    status = customtkinter.CTkLabel(root, text="This is where status will go")
    status.grid(row=2, column=0, sticky="n",  pady=10)
    
    # Place tabview menu at top left
    menu_tab = customtkinter.CTkTabview(root)
    menu_tab.grid(row=0, column=0, sticky="nsew", padx=20, pady=3)
    
    # Create tabview
    tab_main = menu_tab.add("Menu")
    tab_settings = menu_tab.add("Settings")
    
    # Setting up main in tabview
    tab_main_title = customtkinter.CTkLabel(tab_main, text="Hello")
    tab_main_title.pack()
    
    # TODO: Insert main title page (check which columns to show, which location to search, and title) and settings (which columns to show, which amenities to show)
    
    # Place scrollable frame for table
    table_frame = customtkinter.CTkScrollableFrame(root, orientation="vertical")
    table_frame.grid(row=0, column=1, stick="nsew", padx=20, pady=20, rowspan=3)
    
    # TODO: Add a auto generated table
    

def new_insert(root: customtkinter.CTk, status: customtkinter.CTkLabel) -> None:
    """Creates a new window for inserting new listings"""
    insert = customtkinter.CTkToplevel(root)
    insert.attributes("-topmost", True)
    
    # insert Frame
    insert.title("Airbnb | add link")
    
    # Setting up grid
    insert.columnconfigure((1,2,3,4), weight=1)
    insert.rowconfigure(1, weight=3)
    insert.rowconfigure(3, weight=1)

    title = customtkinter.CTkLabel(insert, text="Add a New Listing!")
    title.grid(row=0, column=0, columnspan=4, padx=20, pady=20)
    

    # Link Input
    link_label = customtkinter.CTkLabel(insert, text="Link:")
    link_label.grid(row=1, column=0, sticky="e", padx=20)
    
    link_var = tkinter.StringVar()
    link = customtkinter.CTkEntry(
        insert, placeholder_text="Link", height=40, textvariable=link_var
    )
    link.grid(row=1, column=1, columnspan=3, pady=20, padx=20, sticky="ew")

    # Daily cost input
    cost_label = customtkinter.CTkLabel(insert, text="Cost:")
    cost_label.grid(row=2, column=0, pady=10, sticky="e", padx=20)
    
    cost_var = tkinter.IntVar()
    cost = customtkinter.CTkEntry(
        insert, placeholder_text="Daily Cost", width=100, height=40, textvariable=cost_var
    )
    cost.grid(row=2, column=1, padx=20, pady=10, sticky="w")

    # Miscellaneous cost input
    misc_cost_label = customtkinter.CTkLabel(insert, text="Misc Cost:")
    misc_cost_label.grid(row=2, column=2, pady=10, sticky="e")
    
    misc_cost_var = tkinter.IntVar()
    misc_cost = customtkinter.CTkEntry(
        insert,
        placeholder_text="Miscellaneous Cost",
        width=100,
        height=40,
        textvariable=misc_cost_var,
    )
    misc_cost.grid(row=2, column=3, pady=10, padx=20)

    # Button, which when pressed adds an entry to SQLite using Listing.add_listing()
    button_input = customtkinter.CTkButton(
        insert,
        text="Input",
        command=lambda: (
            Listing.add_listing(
                link.get().strip(),
                [cost.get(), misc_cost.get()],
                status
            ),
            input_clear(link, cost, misc_cost)
        )
    )
    button_input.grid(row=3, column=1, pady=20, padx=20, sticky="e", columnspan=2)
    
    


# BUG Not clearing field
def input_clear(link: customtkinter.CTkEntry, cost: customtkinter.CTkEntry, misc_cost: customtkinter.CTkEntry) -> None:
    """
    Clears the input field in the main box

    Args:
        link (customtkinter.CTkEntry): link field
        cost (customtkinter.CTkEntry): cost field
        misc_cost (customtkinter.CTkEntry): misc cost field
    """
    link.delete(0, customtkinter.END)
    cost.delete(0, customtkinter.END)
    misc_cost.delete(0, customtkinter.END)
    

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
                                        listing_id integer NOT NULL,
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
                                        listing_id integer NOT NULL,
                                        amenities,
                                        images,
                                        notes,
                                        FOREIGN KEY (listing_id) REFERENCES main (id)
                                    ); """

    sql_create_json_table = """ CREATE TABLE IF NOT EXISTS json (
                                        listing_id integer NOT NULL,
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


def sql_add_entry(database: str, items: dict, status: customtkinter.CTkLabel) -> None:
    """
    Adds the entries into the database

    Args:
        database (str): The database for the items to be stored in
        items (dict): Keys are the columns while the values are the entry for each column
        status (customtkinter.Label): For the status
    """

    # TODO: Add status for root
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


def retrieve_from_location(database: str, location: str) -> list:
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


if __name__ == "__main__":
    main()
