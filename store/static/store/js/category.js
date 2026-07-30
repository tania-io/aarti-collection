document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // FILTER DRAWER (open/close)
    // ==========================

    const filterDrawer = document.getElementById("filterDrawer");
    const overlay = document.getElementById("drawerOverlay");

    const filterBtn = document.getElementById("filterBtn");
    const closeDrawer = document.getElementById("closeDrawer");

    function openDrawerMenu() {
        filterDrawer?.classList.add("open");
        overlay?.classList.add("show");
        window.lockBody?.();
    }

    function closeDrawerMenu() {
        filterDrawer?.classList.remove("open");
        overlay?.classList.remove("show");
        window.unlockBody?.();
    }

    filterBtn?.addEventListener("click", openDrawerMenu);
    closeDrawer?.addEventListener("click", closeDrawerMenu);
    overlay?.addEventListener("click", closeDrawerMenu);

    // ==========================
    // FILTER ACCORDION (Price / Category / Colour / Material / Size / Availability / Tags / Purpose)
    // ==========================

    document.querySelectorAll(".filter-section-toggle").forEach(toggle => {

        toggle.addEventListener("click", () => {
            toggle.parentElement.classList.toggle("active");
        });

    });

    // ==========================
    // PRICE SLIDER (only present on product_list / category_products)
    // ==========================

    const minSlider = document.getElementById("minPriceSlider");
    const maxSlider = document.getElementById("maxPriceSlider");

    const minInput = document.getElementById("minPriceInput");
    const maxInput = document.getElementById("maxPriceInput");

    const minLabel = document.getElementById("minPriceLabel");
    const maxLabel = document.getElementById("maxPriceLabel");

    const range = document.querySelector(".price-range");

    if (minSlider && maxSlider && minInput && maxInput && minLabel && maxLabel && range) {

        function updatePriceSlider() {

            let min = parseInt(minSlider.value, 10);
            let max = parseInt(maxSlider.value, 10);

            if (min > max - 100) {
                min = max - 100;
                minSlider.value = min;
            }

            if (max < min + 100) {
                max = min + 100;
                maxSlider.value = max;
            }

            minLabel.textContent = min;
            maxLabel.textContent = max;

            minInput.value = min;
            maxInput.value = max;

            const left = (min / minSlider.max) * 100;
            const right = (max / maxSlider.max) * 100;

            range.style.left = left + "%";
            range.style.width = (right - left) + "%";
        }

        minSlider.addEventListener("input", updatePriceSlider);
        maxSlider.addEventListener("input", updatePriceSlider);
        updatePriceSlider();
    }

    // ==========================
    // SORT MENU
    // ==========================

    const sortBtn = document.getElementById("sortBtn");
    const sortMenu = document.getElementById("sortMenu");

    const sortForm = document.getElementById("sortForm");
    const sortInput = document.getElementById("sortInput");

    sortBtn?.addEventListener("click", (e) => {
        e.stopPropagation();
        sortMenu?.classList.toggle("active");
    });

    document.addEventListener("click", (e) => {

        if (
            sortMenu &&
            !sortMenu.contains(e.target) &&
            !sortBtn?.contains(e.target)
        ) {
            sortMenu.classList.remove("active");
        }

    });

    document.querySelectorAll(".sort-option").forEach(option => {

        option.addEventListener("click", () => {

            if (!sortInput || !sortForm) return;

            sortInput.value = option.dataset.sort;
            sortForm.submit();

        });

    });

    // ==========================
    // ESC KEY — close drawer + sort menu
    // ==========================

    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {
            closeDrawerMenu();
            sortMenu?.classList.remove("active");
        }

    });

});
