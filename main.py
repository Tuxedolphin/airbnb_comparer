import eel
from backend import project

eel.init("./web")

# Keeps track of the stuff that are already saved
location = ""
listings = []

@eel.expose
def update_location(new_location: str) -> None:
    """ Updates the location to be searched """
    
    global location
    global listings
    
    if new_location.lower() != location.lower():
        location = new_location
        listings = project.retrieve_from_location(location)
        
    eel.generateTable(listings)
        
@eel.expose
def get_row(columns: str, listing) -> any:
    """Retrieves the requires columns from the listing """

    row = [["Cover", project.retrieve_from_json("Cover", listing)]] # To make sure that the cover is the first one
    
    for column in columns:
        row.append([column, project.retrieve_from_json(column, listing)])
        
    eel.addRow(row)

@eel.expose
def add_listing(link, daily_price, misc_price) -> None:
    project.add_listing(link, [daily_price, misc_price])

eel.start("index.html")
