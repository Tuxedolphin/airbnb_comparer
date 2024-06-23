import eel
from backend import project

eel.init("./web")


@eel.expose
def get_listings():
    ...
    
@eel.expose
def test():
    print("hello")
    
eel.start("index.html")