const lastMonthTracksButton = document.getElementById('last-month');
const lastSixMonthsTracksButton = document.getElementById('last-six-months');
const lastMonthTracksData = document.getElementById('last-month-tracks');
const lastSixMonthsTracksData = document.getElementById('last-six-months-tracks');

let lastMonthClicked = false;
let lastSixMonthsClicked = false;

lastMonthTracksButton.addEventListener('click', () => {
    lastMonthClicked = true;
    lastSixMonthsClicked = false;
    toggleDisplay();
});

lastSixMonthsTracksButton.addEventListener('click', () => {
    lastSixMonthsClicked = true;
    lastMonthClicked = false;
    toggleDisplay();
});

function toggleDisplay() {
    lastMonthTracksData.style.display = lastMonthClicked ? "block" : "none";
    lastSixMonthsTracksData.style.display = lastSixMonthsClicked ? "block" : "none";
}
