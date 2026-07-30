document.addEventListener("DOMContentLoaded", () => {

    const isMobile = () => window.matchMedia("(max-width:991px)").matches;

    const columns = document.querySelectorAll(".footer-column");

    document.querySelectorAll(".footer-heading").forEach(heading => {

        heading.addEventListener("click", () => {

            if (!isMobile()) return;

            const column = heading.closest(".footer-column");

            if (!column) return;

            const willOpen = !column.classList.contains("open");

            // Only one section open at a time.
            columns.forEach(c => c.classList.remove("open"));

            if (willOpen) {
                column.classList.add("open");
            }

        });

    });

});
