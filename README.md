# AIRBNB LISTING COMPARER

This is an application which scrapes the listing to automatically insert most of the information from a listing and stores it into a database. A user can then easily compare and search for the listings that he so desires, which will dynamically generate a table.

## Getting Started

### Prerequisites

Before installing the program, make sure the following is done:
1. Please make sure that you have Python3 installed on your device.
2. Please read the [bug fixes](#bug-fixes).

### Installation

Please install the entire directory, either directly from this repository or by creating your own fork of the repository.

After installing the folder, run the following in this directory to install all of the extensions used:

```
pip install -r requirements.txt
```

Thereafter, run the file `main.py`, either from the terminal or using a code editor. Please note that you are likely to face the error `ModuleNotFoundError: No module named 'bottle.ext.websocket'`. If you do, please refer to [bug fixes](#bug-fixes).

## Navigating The UI

### Adding A Listing

After running the file, the following page should appear:

![airbnb-main](https://github.com/user-attachments/assets/3d767c0d-6401-46a8-8ae0-b980d376090f)

To add a listing, click on the `Add Listing` button. Then, there will be a pop-up as shown:

![airbnb-add](https://github.com/user-attachments/assets/e8367b70-7731-4663-bf4c-2596c9246509)

Insert the link of the listing that you want to add, its daily cost, and the miscellaneous costs (includes cleaning fee and service fees). After you are done, click teh `Add` button, and the rest of the information will be automatically retrieved.

> [!NOTE]
> Please choose the dates that you want to stay at at the listing website before copying the link. This is because the program retrieves the dates from the URL and uses it to calcualte the duration of stay and the total costs.

### Viewing Listings

To view the listings, navigate to the `Insert location` textbox and key in the location that you want to search by. Then, click on the checkboxes corresponding to the parameters that you want to compare by. Then, click on the `Submit` button and a table will be automatically generated:

![airbnb-table](https://github.com/user-attachments/assets/243e4a62-39fe-49c0-9679-1b5ad33566ad)

Note that the cover is always shown. This is to ensure that the user is able to easily identify which listing it is. To view the images belonging to the listing, click on the `See Images` button, which will open up the following:

![airbnb-images](https://github.com/user-attachments/assets/f258fa0a-1af7-4176-b9c1-88c3841cbe4a)

This includes all of the images of the listing. You can simply scroll down to view all of the photos. To exit the screen, press the `Esc` key.

## Bug Fixes

If you have encountered the error `ModuleNotFoundError: No module named 'bottle.ext.websocket'`, you can refer to the video as follows: `https://youtu.be/uOdp_E1vL68?si=vPV6tK98I_Mv6s1M`.

This bug is caused by the newest version of Python 3 causing an error with the eel extension, and is unfortunately not fixes by the eel developers.
