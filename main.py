import eel
from backend import project

eel.init("./web")


@eel.expose
def get_listings(location) -> list:
    """ Returns a list of dictionaries """
    return project.retrieve_from_location(location)
    
@eel.expose
def add_listing(link, daily_price, misc_price) -> None:
    project.add_listing(link, [daily_price, misc_price])
    
 
eel.start("index.html")