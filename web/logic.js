let menuButton = document.querySelector("#menu-button");
let addButton = document.querySelector("#add-button");
let settingsButton = document.querySelector("#settings-button");
let searchLocation = document.querySelector("#search-location");
let filters = document.querySelectorAll(".input-group > input");
let displayTable = document.querySelector("table");
let dialog = document.querySelector("dialog");

let currentLocation = "";
let listings;

// All of the different columns
let checkboxID = new Map([
    ["ID", "id"],
    ["Rating", "rating"],
    ["URL", "url"],
    ["Duration", "duration"],
    ["location", "location"],
    ["Getting Around", "getting-around"],
    ["Check In/ Out Timing", "check-in-out"],
    ["Layout", "layout"],
    ["Capacity", "capacity"],
    ["Cost", "cost"],
    ["Super Host", "super-host"],
    ["Amenities", "amenities"],
    ["Notes", "notes"],
    ["Images", "images"],
    ["Cover", "cover"],
])

// Adding functionalities for all the buttons
menuButton.addEventListener("click", (e) => {

    // Only look for listings if the location is different
    if (currentLocation.toLowerCase() !== searchLocation.value.toLowerCase()) {
        currentLocation = searchLocation.value;
        listings = eel.get_listings(currentLocation);
    }

    generateTable(listings);

});

addButton.addEventListener("click", (e) => {
    dialog.showModal();
});

settingsButton.addEventListener("click", (e) => {
    menu = document.querySelector(".menu");
    menuElements = document.querySelectorAll(".menu > *");

    // Hides the original elements
    menu.style.display = "none";

    settings = document.querySelector(".settings");
    settingElements = document.querySelectorAll(".settings > *");

    // Makes the elements of settings visible
    settings.style.display = "grid";
});

// Adding functionalities for buttons of the modal
let modalAddButton = document.querySelector("#addButton");
let modalCancelButton = document.querySelector("#cancelButton");

modalAddButton.addEventListener("click", (e) => {

    // Adds the provided information into SQL database
    link = dialog.querySelector("#link").value;
    dailyPrice = dialog.querySelector("#dailyPrice");
    miscPrice = dialog.querySelector("#MiscPrice");
    dialog.querySelector(".add-listing").reset();
    dialog.close();

    eel.add_listing(link, dailyPrice, miscPrice);

});

modalCancelButton.addEventListener("click", (e) => {

    // Closes the modal and clears the form
    document.querySelector(".add-listing").reset();
    dialog.close();

});

// Selects the table for automatic table generation
let listingTable = document.querySelector("#listing-table");
let tableHeader = listingTable.querySelector("thead > tr");
let tableBody = listingTable.querySelector("tbody");

// Dynamically generates the table using the required information
function generateTable(listingDicts) {

    let columnsSelected = [];

    // Loops through the checkboxes and selects those which are checked
    checkboxID.forEach((id, columnName) => {
        if (document.getElementById(id).checked) {
            let newHeader = document.createElement("th");
            newHeader.textContent = columnName;
            tableHeader.appendChild(newHeader);

            columnsSelected.push(columnName);
        }
    });

    listingDicts.forEach((listing) => {
        let newRow = document.createElement("tr");
        tableBody.appendChild(newRow);

        let newCell = document.createElement("td");
        newCell.textContent = listing;
        newRow.appendChild(newCell);

        columnsSelected.forEach((column) => {
            newCell = document.createElement("td");
            newCell.textContent = eel.retrieve_from_json(column, listing);
            newRow.appendChild(newCell);
        });
    })
}