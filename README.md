# AUTOMATIC AIRBNB COMPARER

## Video Demo

`https://youtu.be/I9ZvV8Vgxog`

## Description

### Problem

When browsing airbnb listings and choosing which listing to go for, it can often be
difficult to choose and compare which listing one wants. After all - they all look pretty
good, don't they? Inputting all the information into an excel spreadsheet is also often
troublesome and annoying, and frankly takes maybe way too long. Hence, I created an desktop
app to try to address the situation.

### Specifications

To add a listing, one simply presses the add a listing option. A new page pops up which
requires a user to input the link (with the id, check in and check out dates), the (daily)
cost, and miscellaneous costs (airbnb service charge + cleaning fee). The entry is then
automatically entered into a SQLite3 database for storage.

To compare, simply go to the main page and input the location that one wants to compare the
listings for. Then, using the checkboxes, select the columns that one wants to show. After pressing
submit, the app automatically retrieves the required listings and displays the columns selected
in a dynamically generated table.

### Languages used

Python
SQLite3

## Bug Fixes

If one has encountered the error `ModuleNotFoundError: No module named 'bottle.ext.websocket'`, you can
refer to the video as follows:
`https://youtu.be/uOdp_E1vL68?si=vPV6tK98I_Mv6s1M`
