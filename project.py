import gobnb, json, tkinter, customtkinter, sqlite3, re, sys
from datetime import datetime


def main():
    app = customtkinter.CTk()
    tkinter_set_up(app)

    ## Setting up the main page of UI
    # UI elements
    title = customtkinter.CTkLabel(app, text="Insert Location")
    title.pack(padx=10, pady=10)

    # Location Input
    link_var = tkinter.StringVar()
    link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=link_var)
    link.pack()

    # Button
    button_input = customtkinter.CTkButton(
        app, text="Input", command=lambda: listing_adder(link.get().strip())
    )
    button_input.pack(pady=10)

    app.mainloop()


def tkinter_set_up(app):
    """
    Sets up tkinter
    """

    # System Settings
    customtkinter.set_appearance_mode("system")
    customtkinter.set_default_color_theme("blue")

    # App Frame
    app.geometry("720x480")
    app.title("AirBnB")


def listing_adder(
    link: str,
    currency="SGD",
):
    """
    Adds the listing to a json file for analysis (more for myself), before storing in sqlite database
    """

    # Search through url for required information - id, check in and check out date
    match = re.search(
        r"^https:\/\/www\.airbnb\.com(?:\.sg)?\/rooms\/(\d+)\?.*check_in=(.{10}).*check_out=(.{10})",
        link,
    )

    # In case of invalid URL which does not contain the required information
    try:
        id = match.group(1)
        check_in = datetime.fromisoformat(match.group(2))
        check_out = datetime.fromisoformat(match.group(3))
    except ValueError:
        sys.exit("Invalid Link: make sure to choose date")
    else:
        timedelta = check_out - check_in

    # Scrape the listing for the required information, except cost (AirBnB website is >:( )
    data = gobnb.Get_from_room_url(link, currency, "")

    # Format and export into json file for myself to see + analyse into sqlite
    jsondata = json.dumps(data, indent=4)
    with open("result.json", "w") as file:
        file.write(jsondata)

    # Call function to add required information into SQL database
    add_listing_sql(id, timedelta)


def add_listing_sql(id, timedelta):
    """
    To store into sqlite database
    """
    with open("result.json", "r") as file:
        data = json.load(file)
    
    


if __name__ == "__main__":
    main()
