import eel
from backend import project

eel.init("./web")


@eel.expose
def get_listings(location):
    return project.retrieve_from_location(location)
    
@eel.expose
def add_listing(link, daily_price, misc_price) -> None:
    ...
    
 
eel.start("index.html")