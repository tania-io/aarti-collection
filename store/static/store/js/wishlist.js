document.addEventListener("DOMContentLoaded", () => {

    // BUG FIX: this page has no {% csrf_token %} form field, so relying
    // only on a form input left csrfToken as `undefined` and every
    // wishlist AJAX action (remove, remove all, move to cart, share...)
    // was silently rejected by Django's CSRF check. Fall back to the
    // csrftoken cookie (always set, since base.html renders csrf_token).
    const csrfToken =
        document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
        window.getCookie?.("csrftoken");

    document.querySelectorAll(".wishlist-toggle").forEach(button => {

        button.addEventListener("click", async (event) => {

            event.preventDefault();

            const image = button.querySelector(".wishlist-heart");
            const wishlistRow = button.closest(".wishlist-item");

            const isActive = button.classList.contains("active");

            const url = isActive
                ? button.dataset.removeUrl
                : button.dataset.addUrl;

            try {

                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                if (!response.ok)
                    throw new Error("Wishlist request failed.");

                const data = await response.json();

                if (!data.success)
                    return;

                // Remove button inside the wishlist popup: drop the row
                // and update the header count instead of toggling a heart.
                if (wishlistRow && !image) {

                    wishlistRow.remove();

                    const countBadge = document.querySelector(".wishlist-count");

                    if (countBadge) {

                        const remaining = document.querySelectorAll(".wishlist-item").length;

                        if (remaining > 0) {
                            countBadge.textContent = remaining;
                        } else {
                            countBadge.remove();
                        }

                    }

                    return;

                }

                button.classList.toggle("active");

                if (image) {

                    image.src = button.classList.contains("active")
                        ? "/static/store/icons/heart.svg"
                        : "/static/store/icons/wishlist.svg";

                }

            } catch (error) {

                console.error(error);

            }

        });

    });

    // ==========================
    // WISHLIST PAGE — remove item
    // ==========================

    document.querySelectorAll(".wishlist-remove-btn").forEach(button => {

        button.addEventListener("click", async () => {

            const card = button.closest(".wishlist-card");

            try {
                const response = await fetch(button.dataset.removeUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                const data = await response.json();
                if (data.success) {
                    card?.remove();
                    updateBulkBar();
                    syncWishlistHeaderCount();
                    maybeShowEmptyState();
                }

            } catch (error) {
                console.error(error);
            }

        });

    });

    // ==========================
    // WISHLIST PAGE — move to cart
    // ==========================

    document.querySelectorAll(".wishlist-move-to-cart").forEach(button => {

        button.addEventListener("click", async () => {

            const card = button.closest(".wishlist-card");
            button.disabled = true;
            button.textContent = "Adding…";

            try {
                const addResponse = await fetch(button.dataset.addUrl, {
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                });
                const addData = await addResponse.json();

                if (typeof addData.cart_count !== "undefined") {
                    document.querySelectorAll(".cart-count").forEach(el => {
                        el.textContent = addData.cart_count;
                        el.style.display = addData.cart_count > 0 ? "flex" : "none";
                    });
                }

                window.showAddToCartToast?.({ product_name: addData.product_name });

                const removeResponse = await fetch(button.dataset.removeUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                const data = await removeResponse.json();
                if (data.success) {
                    card?.remove();
                    updateBulkBar();
                    syncWishlistHeaderCount();
                    maybeShowEmptyState();
                }

            } catch (error) {
                console.error(error);
                button.disabled = false;
                button.textContent = "Move to Cart";
            }

        });

    });

    // ==========================
    // WISHLIST PAGE — sort
    // ==========================

    document.getElementById("wishlistSort")?.addEventListener("change", function () {
        const url = new URL(window.location.href);
        url.searchParams.set("sort", this.value);
        window.location.href = url.toString();
    });

    // ==========================
    // WISHLIST PAGE — select all / bulk bar
    // ==========================

    const selectAll = document.getElementById("wishlistSelectAll");
    const itemCheckboxes = () => document.querySelectorAll(".wishlist-item-checkbox");
    const bulkBar = document.getElementById("wishlistBulkBar");
    const selectedCountEl = document.getElementById("wishlistSelectedCount");

    function updateBulkBar() {
        const checked = document.querySelectorAll(".wishlist-item-checkbox:checked");
        if (selectedCountEl) selectedCountEl.textContent = checked.length;
        bulkBar?.classList.toggle("show", checked.length > 0);

        if (selectAll) {
            const all = itemCheckboxes();
            selectAll.checked = all.length > 0 && checked.length === all.length;
        }
    }

    selectAll?.addEventListener("change", function () {
        itemCheckboxes().forEach(cb => { cb.checked = this.checked; });
        updateBulkBar();
    });

    document.addEventListener("change", (e) => {
        if (e.target.classList.contains("wishlist-item-checkbox")) updateBulkBar();
    });

    function getSelectedIds() {
        return Array.from(document.querySelectorAll(".wishlist-item-checkbox:checked"))
            .map(cb => cb.value);
    }

    async function postBulkAction(action, productIds) {
        try {
            const response = await fetch("/wishlist/bulk-action/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ action, product_ids: productIds }),
            });
            return await response.json();
        } catch (error) {
            console.error(error);
            return { success: false };
        }
    }

    function removeCardsForIds(ids) {

        ids.forEach(id => {
            document.getElementById(`wishlist-item-${id}`)?.remove();
        });

        updateBulkBar();
        syncWishlistHeaderCount();
        maybeShowEmptyState();

    }

    function removeAllCards() {

        document.querySelectorAll(".wishlist-card").forEach(card => card.remove());
        updateBulkBar();
        syncWishlistHeaderCount();
        maybeShowEmptyState();

    }

    function syncWishlistHeaderCount() {

        const remaining = document.querySelectorAll(".wishlist-card").length;

        document.querySelectorAll(".wishlist-count").forEach(el => {
            el.textContent = remaining;
            el.style.display = remaining > 0 ? "flex" : "none";
        });

        const itemCountLine = document.querySelector(".page-header p");
        if (itemCountLine) {
            itemCountLine.textContent = `${remaining} item${remaining === 1 ? "" : "s"} saved`;
        }

    }

    function maybeShowEmptyState() {

        const grid = document.querySelector(".wishlist-grid");
        if (grid && grid.children.length === 0) {
            window.location.reload();
        }

    }

    document.getElementById("wishlistRemoveAllBtn")?.addEventListener("click", async () => {
        if (!window.confirm("Remove everything from your wishlist?")) return;
        const data = await postBulkAction("remove_all", []);
        if (data.success) removeAllCards();
    });

    document.getElementById("wishlistMoveAllBtn")?.addEventListener("click", async () => {
        const data = await postBulkAction("move_all_to_cart", []);
        if (data.success) {
            if (typeof data.cart_count !== "undefined") {
                document.querySelectorAll(".cart-count").forEach(el => {
                    el.textContent = data.cart_count;
                    el.style.display = data.cart_count > 0 ? "flex" : "none";
                });
            }
            removeAllCards();
        }
    });

    document.getElementById("wishlistRemoveSelectedBtn")?.addEventListener("click", async () => {
        const ids = getSelectedIds();
        if (!ids.length) return;
        const data = await postBulkAction("remove_selected", ids);
        if (data.success) removeCardsForIds(ids);
    });

    document.getElementById("wishlistMoveSelectedBtn")?.addEventListener("click", async () => {
        const ids = getSelectedIds();
        if (!ids.length) return;
        const data = await postBulkAction("move_selected_to_cart", ids);
        if (data.success) {
            if (typeof data.cart_count !== "undefined") {
                document.querySelectorAll(".cart-count").forEach(el => {
                    el.textContent = data.cart_count;
                    el.style.display = data.cart_count > 0 ? "flex" : "none";
                });
            }
            removeCardsForIds(ids);
        }
    });

    // ==========================
    // WISHLIST PAGE — share / copy link / email
    // ==========================

    const shareModal = document.getElementById("wishlistShareModal");
    const shareUrlInput = document.getElementById("wishlistShareUrl");
    const emailBtn = document.getElementById("wishlistEmailBtn");

    document.getElementById("wishlistShareBtn")?.addEventListener("click", async () => {

        try {
            const response = await fetch("/wishlist/share-link/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const data = await response.json();

            if (data.success && shareUrlInput) {
                shareUrlInput.value = data.share_url;
                if (emailBtn) {
                    emailBtn.href =
                        `mailto:?subject=${encodeURIComponent("Check out my wishlist!")}` +
                        `&body=${encodeURIComponent("Take a look at my Aarti Collection wishlist: " + data.share_url)}`;
                }
                shareModal?.classList.add("show");
            }
        } catch (error) {
            console.error(error);
        }

    });

    document.getElementById("wishlistShareClose")?.addEventListener("click", () => {
        shareModal?.classList.remove("show");
    });

    shareModal?.addEventListener("click", (e) => {
        if (e.target === shareModal) shareModal.classList.remove("show");
    });

    document.getElementById("wishlistCopyLinkBtn")?.addEventListener("click", function () {
        if (!shareUrlInput?.value) return;
        navigator.clipboard?.writeText(shareUrlInput.value).then(() => {
            const original = this.textContent;
            this.textContent = "Copied!";
            setTimeout(() => { this.textContent = original; }, 1500);
        });
    });

});