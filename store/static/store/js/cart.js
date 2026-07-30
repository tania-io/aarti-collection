document.addEventListener("DOMContentLoaded", () => {

    const csrftoken =
        document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
        getCookie("csrftoken");

    const toast = document.getElementById("cartToast");
    const toastName = document.getElementById("cartToastName");

    const drawerBody = document.getElementById("cartDrawerBody");
    const drawer = document.getElementById("cartDrawer");
    const tableBody = document.getElementById("cartTableBody");
    const tableOuter = document.querySelector(".cart-page-table-outer");

    let toastTimer = null;

    // --------------------------
    // Helpers
    // --------------------------

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            for (let cookie of document.cookie.split(";")) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function setLoading(isLoading) {
        drawer?.classList.toggle("loading", isLoading);
        tableOuter?.classList.toggle("loading", isLoading);
    }

    function updateCartBadge(count) {
        document.querySelectorAll(".cart-count").forEach(el => {
            el.textContent = count;
            el.style.display = count > 0 ? "flex" : "none";
        });
    }

    function updateSubtotal(subtotal) {
        document.querySelectorAll("[data-cart-subtotal]").forEach(el => {
            el.textContent = `₹${subtotal}`;
        });
    }

    // Every cart-mutating response has the same shape (see _cart_payload
    // in views.py) — this is the ONLY place that writes cart HTML into
    // the page, so the drawer and the full /cart/ page can never drift
    // out of sync with each other or with the server.
    function applyCartPayload(data) {
        if (!data) return;

        if (typeof data.cart_count !== "undefined") updateCartBadge(data.cart_count);
        if (typeof data.subtotal !== "undefined") updateSubtotal(data.subtotal);

        if (drawerBody && typeof data.drawer_html === "string") {
            drawerBody.innerHTML = data.drawer_html;
        }

        if (tableBody && typeof data.table_html === "string") {
            tableBody.innerHTML = data.table_html;
        }
    }

    function showCartToast(data) {
        if (!toast) return;
        toastName.textContent = data.product_name
            ? `${data.product_name} added to cart`
            : "Product added to cart";

        toast.classList.remove("active"); // restart animation if triggered again quickly
        void toast.offsetWidth; // force reflow
        toast.classList.add("active");

        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {
            toast.classList.remove("active");
        }, 2500);
    }

    window.showAddToCartToast = showCartToast;

    function postJSON(url) {
        return fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
            },
        }).then(res => res.json());
    }

    // --------------------------
    // Add to Cart (AJAX) + toast
    // --------------------------

    function addToCartAjax(url, qty, variantId) {
        const params = new URLSearchParams();
        params.set("qty", qty || 1);
        if (variantId) params.set("variant_id", variantId);

        const finalUrl = url + (url.includes("?") ? "&" : "?") + params.toString();

        setLoading(true);

        return fetch(finalUrl, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    applyCartPayload(data);
                    showCartToast(data);
                } else if (data.error === "login_required") {
                    window.location.href = "/login/?next=" + encodeURIComponent(window.location.pathname);
                }
                return data;
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }

    document.querySelectorAll("a.cart-icon, a.pg-cart-btn, a.wishlist-cart-btn").forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            addToCartAjax(this.getAttribute("href"), 1, this.dataset.variantId);
        });
    });

    // Product detail "Add to Cart" button (uses selected quantity + variant)
    const addCartBtn = document.querySelector(".add-cart-btn");

    addCartBtn?.addEventListener("click", function () {
        const qtyInput = document.getElementById("qty");
        const qty = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
        const url = this.dataset.url;
        if (!url) return;
        addToCartAjax(url, qty, this.dataset.variantId);
    });

    // --------------------------
    // Increase / Decrease / Remove — delegated so buttons keep working
    // after the drawer/table are re-rendered with fresh HTML
    // --------------------------

    document.addEventListener("click", function (e) {

        const increaseBtn = e.target.closest(".increase-btn");
        const decreaseBtn = e.target.closest(".decrease-btn");
        const removeBtn = e.target.closest(".remove-btn");

        if (!increaseBtn && !decreaseBtn && !removeBtn) return;

        e.preventDefault();

        const btn = increaseBtn || decreaseBtn || removeBtn;
        const itemId = btn.dataset.id;
        if (!itemId) return;

        let endpoint = "increase";
        if (decreaseBtn) endpoint = "decrease";
        if (removeBtn) endpoint = "remove";

        setLoading(true);

        postJSON(`/cart/${endpoint}/${itemId}/`)
            .then(data => applyCartPayload(data))
            .catch(() => {})
            .finally(() => setLoading(false));
    });

    // --------------------------
    // Gift note (full cart page) — autosave on blur
    // --------------------------

    document.addEventListener("blur", function (e) {

        const input = e.target.closest?.(".cart-note-input");
        if (!input) return;

        const itemId = input.dataset.id;
        if (!itemId) return;

        const body = new URLSearchParams();
        body.set("note", input.value);

        fetch(`/cart/note/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: body.toString(),
        })
            .then(res => res.json())
            .then(data => applyCartPayload(data))
            .catch(() => {});

    }, true);

    // Note: the drawer's "Copy Link" button is already wired up in
    // main.js's initializeCartDrawer() — keeping that as the single
    // source of truth instead of duplicating it here.

});
