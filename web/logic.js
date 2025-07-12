// Selects all of the stuff
let menuButton = document.querySelector("#menu-button");
let addButton = document.querySelector("#add-button");
let settingsButton = document.querySelector("#settings-button");
let searchLocation = document.querySelector("#search-location");
let filters = document.querySelectorAll(".input-group > input");
let displayTable = document.querySelector("table");
let dialog = document.querySelector("dialog#add-listing");

let currentLocation = "";
let listings;

// All of the different columns
let checkboxID = new Map([
  ["ID", "id"],
  ["Rating", "rating"],
  ["URL", "url"],
  ["Duration", "duration"],
  ["Location", "location"],
  ["Getting Around", "getting-around"],
  ["Check In/ Out Timing", "check-in-out"],
  ["Layout", "layout"],
  ["Capacity", "capacity"],
  ["Cost", "cost"],
  ["Super Host", "super-host"],
  ["Amenities", "amenities"],
  ["Highlights", "highlights"],
  ["Reviews Summary", "reviews-summary"],
  ["House Rules", "house-rules"],
  ["Property Details", "property-details"],
  ["Notes", "notes"],
  ["Images", "images"],
]);

// Adding functionalities for all the buttons
menuButton.addEventListener("click", (e) => {
  eel.update_location(searchLocation.value.toLowerCase());
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

  eel.add_listing(link);
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
eel.expose(generateTable);
function generateTable(listingDicts) {
  // Clears the original table to prevent duplicates
  tableHeader.replaceChildren();
  tableBody.replaceChildren();

  let columnsSelected = [];

  let newHeader = document.createElement("th");
  newHeader.textContent = "Cover";
  tableHeader.appendChild(newHeader);

  // Loops through the checkboxes and selects those which are checked
  checkboxID.forEach((id, columnName) => {
    if (document.getElementById(id).checked) {
      newHeader = document.createElement("th");
      newHeader.textContent = columnName;
      tableHeader.appendChild(newHeader);

      columnsSelected.push(columnName);
    }
  });

  // Creates a new row for each listing
  for (listing of listingDicts) {
    eel.get_row(columnsSelected, listing);
  }
}

// Dynamically adds a row to the table generated
eel.expose(addRow);
function addRow(row) {
  let newRow = document.createElement("tr");
  tableBody.appendChild(newRow);

  row.forEach((array) => {
    let newCell = document.createElement("td");
    newRow.appendChild(newCell);

    let [type, content] = array;

    // Tidies up the type of content and filters them to make it more readable
    switch (type) {
      case "Cover":
        var newSubCell = document.createElement("img");
        newSubCell.src = content;
        newCell.appendChild(newSubCell);
        break;

      case "Rating":
        newCell.textContent = Math.round(content * 100) / 100;
        break;

      case "URL":
        var newSubCell = document.createElement("a");
        newSubCell.href = content;
        let newButton = document.createElement("button");
        newButton.textContent = "View Listing";
        newCell.appendChild(newSubCell);
        newSubCell.appendChild(newButton);
        break;

      case "Duration":
        newCell.textContent = content + " days";
        break;

      case "Capacity":
        newCell.textContent = content + " people";
        break;

      case "Check In/ Out Timing":
        let newParagraph;
        content.forEach((value) => {
          newParagraph = document.createElement("p");
          newParagraph.textContent = value;
          newCell.appendChild(newParagraph);
        });
        break;

      case "Layout":
        var newSubCell = document.createElement("ul");
        newCell.appendChild(newSubCell);

        let newListElement;
        content[0].forEach((content) => {
          newListElement = document.createElement("li");
          newListElement.textContent = content;
          newSubCell.appendChild(newListElement);
        });
        break;

      case "Cost":
        newCell.textContent = "$" + content;
        break;

      case "Super Host":
        newCell.textContent = content === "true" ? "Yes" : "No";
        break;

      case "Amenities":
        // Initialise all of these first for use in loop
        newCell.classList = "amenities";
        let amenitiesContainer = document.createElement("div");
        amenitiesContainer.classList = "amenities";
        newCell.appendChild(amenitiesContainer);

        let newHeaderList = document.createElement("ol");
        amenitiesContainer.appendChild(newHeaderList);
        let newHeader;
        let newItemList;
        let newItem;

        // Create a nested list of lists
        for (const [header, items] of Object.entries(content)) {
          newHeader = document.createElement("li");
          newHeader.textContent = header;
          newHeaderList.appendChild(newHeader);

          newItemList = document.createElement("ul");
          newHeader.appendChild(newItemList);

          items.forEach((item) => {
            newItem = document.createElement("li");
            newItem.textContent = item;
            newItemList.appendChild(newItem);
          });
        }
        break;

      case "Highlights":
        var newSubCell = document.createElement("ul");
        newCell.appendChild(newSubCell);

        let highlightListElement;
        content.forEach((highlight) => {
          highlightListElement = document.createElement("li");
          highlightListElement.textContent = highlight;
          newSubCell.appendChild(highlightListElement);
        });
        break;

      case "Reviews Summary":
        newCell.classList = "reviews-summary";
        let reviewsContainer = document.createElement("div");
        reviewsContainer.classList = "reviews-summary";
        newCell.appendChild(reviewsContainer);

        let totalReviews = document.createElement("p");
        totalReviews.textContent = `Total Reviews: ${content.total_reviews}`;
        reviewsContainer.appendChild(totalReviews);

        if (content.recent_reviews && content.recent_reviews.length > 0) {
          let recentHeader = document.createElement("h4");
          recentHeader.textContent = "Recent Reviews:";
          reviewsContainer.appendChild(recentHeader);

          content.recent_reviews.forEach((review) => {
            let reviewDiv = document.createElement("div");
            reviewDiv.classList = "review-item";

            let rating = document.createElement("span");
            rating.textContent = `Rating: ${review.rating}/5`;
            rating.classList = "review-rating";

            let comment = document.createElement("p");
            comment.textContent = review.comment;
            comment.classList = "review-comment";

            let date = document.createElement("span");
            date.textContent = review.date;
            date.classList = "review-date";

            reviewDiv.appendChild(rating);
            reviewDiv.appendChild(comment);
            reviewDiv.appendChild(date);
            reviewsContainer.appendChild(reviewDiv);
          });
        }
        break;

      case "House Rules":
        newCell.classList = "house-rules";
        let rulesContainer = document.createElement("div");
        rulesContainer.classList = "house-rules";
        newCell.appendChild(rulesContainer);

        if (content.check_in_out && content.check_in_out.length > 0) {
          let checkInHeader = document.createElement("h4");
          checkInHeader.textContent = "Check-in/Check-out:";
          rulesContainer.appendChild(checkInHeader);

          let checkInList = document.createElement("ul");
          content.check_in_out.forEach((rule) => {
            let listItem = document.createElement("li");
            listItem.textContent = rule;
            checkInList.appendChild(listItem);
          });
          rulesContainer.appendChild(checkInList);
        }

        if (content.general_rules && content.general_rules.length > 0) {
          content.general_rules.forEach((ruleGroup) => {
            let groupHeader = document.createElement("h4");
            groupHeader.textContent = ruleGroup.category + ":";
            rulesContainer.appendChild(groupHeader);

            let groupList = document.createElement("ul");
            ruleGroup.rules.forEach((rule) => {
              let listItem = document.createElement("li");
              listItem.textContent = rule;
              groupList.appendChild(listItem);
            });
            rulesContainer.appendChild(groupList);
          });
        }

        if (content.additional_rules && content.additional_rules[0]) {
          let additionalHeader = document.createElement("h4");
          additionalHeader.textContent = "Additional Rules:";
          rulesContainer.appendChild(additionalHeader);

          let additionalText = document.createElement("p");
          additionalText.textContent = content.additional_rules[0];
          rulesContainer.appendChild(additionalText);
        }
        break;

      case "Property Details":
        newCell.classList = "property-details";
        let detailsContainer = document.createElement("div");
        detailsContainer.classList = "property-details";
        newCell.appendChild(detailsContainer);

        let roomType = document.createElement("p");
        roomType.textContent = `Room Type: ${content.room_type}`;
        detailsContainer.appendChild(roomType);

        let guestFavorite = document.createElement("p");
        guestFavorite.textContent = `Guest Favorite: ${
          content.is_guest_favorite ? "Yes" : "No"
        }`;
        detailsContainer.appendChild(guestFavorite);

        if (content.layout && content.layout.length > 0) {
          let layoutHeader = document.createElement("h4");
          layoutHeader.textContent = "Layout:";
          detailsContainer.appendChild(layoutHeader);

          let layoutList = document.createElement("ul");
          content.layout.forEach((item) => {
            let listItem = document.createElement("li");
            listItem.textContent = item;
            layoutList.appendChild(listItem);
          });
          detailsContainer.appendChild(layoutList);
        }
        break;

      case "Images":
        var newSubCell = document.createElement("button");
        newSubCell.textContent = "See Images";
        let newImage;
        newSubCell.addEventListener("click", (e) => {
          let imagesDialog = document.querySelector("#show-images");
          imagesDialog.showModal();

          content.forEach((imageLink) => {
            newImage = document.createElement("img");
            newImage.src = imageLink;
            imagesDialog.appendChild(newImage);
          });
        });
        newCell.appendChild(newSubCell);
        break;

      default:
        console.log(content);
        newCell.textContent = content;
    }
  });

  // Adds the edit button at the very end
  newCell = document.createElement("td");
  newRow.appendChild(newCell);

  let editButton = document.createElement("button");
  editButton.classList = "edit";

  let editSymbol = document.createElement("i");
  editSymbol.classList = "fa fa-edit";

  newCell.appendChild(editButton);
  editButton.appendChild(editSymbol);
}
