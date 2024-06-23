function getListings() {
    return eel.get_listings();
}

let button = document.querySelector("#menu-button");
let searchLocation = document.querySelector("#search-location")
let filters = document.querySelectorAll(".input-group > input")

button.addEventListener("click", (e) => {
    console.log(searchLocation.value)
    console.log(filters[0].value)
});