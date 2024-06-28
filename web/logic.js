let menuButton = document.querySelector("#menu-button");
let addButton = document.querySelector("#add-button");
let settingsButton = document.querySelector("#settings-button");
let searchLocation = document.querySelector("#search-location");
let filters = document.querySelectorAll(".input-group > input");
let displayTable = document.querySelector("table");
let dialog = document.querySelector("dialog");

let currentLocation;
let listings;

// Adding functionalities for all the buttons
menuButton.addEventListener("click", (e) => {

    // Only look for listings if the location is different
    if (currentLocation.toLowerCase() !== searchLocation.value.toLowerCase()) {
        currentLocation = searchLocation.value;
        listings = eel.get_listings(currentLocation);
    }
    
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
listingTable = document.querySelector("#listing-table");
tableHeader = listingTable.querySelector("thead > tr");
tableBody = listingTable.querySelector("tbody");

// Dynamically generates the table using the required information
function generateTable(listingDicts, columns) {

    for (column of column) {
        newHeader = document.createElement("th");
        newHeader.textContent = column;
        tableHeader.appendChild(newHeader);
    }

    for (listing of listingDicts) {
        
    }
}