document.addEventListener("DOMContentLoaded", () => {
    const counter = document.getElementById("visitor-count");

    if (!counter) {
        return;
    }

    fetch("/api/visitors", {
        method: "GET",
        cache: "no-store"
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Visitor counter unavailable");
            }
            return response.json();
        })
        .then((data) => {
            if (Number.isFinite(data.visits)) {
                counter.textContent = new Intl.NumberFormat().format(data.visits);
            }
        })
        .catch(() => {
            // Keep the neutral placeholder if the counter service is unavailable.
        });
});
