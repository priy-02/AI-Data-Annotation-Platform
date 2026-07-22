const searchInput = document.getElementById("searchInput");

const cards = document.querySelectorAll(".image-card");

let currentFilter = "all";

function applyFilters() {

    const searchValue = searchInput.value.toLowerCase();

    cards.forEach(card => {

        const filename = card.dataset.name;
        const status = card.dataset.status;

        const searchMatch = filename.includes(searchValue);

        const statusMatch =
            currentFilter === "all" ||
            status === currentFilter;

        if (searchMatch && statusMatch) {

            card.style.display = "block";

        } else {

            card.style.display = "none";

        }

    });

}

searchInput.addEventListener("keyup", applyFilters);

function filterImages(status) {

    currentFilter = status;

    applyFilters();

}