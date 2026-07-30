document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector(".checkout-form");

    if (!form) return;

    const phone = form.querySelector("input[name='phone']");
    const name = form.querySelector("input[name='name']");
    const address = form.querySelector("textarea[name='address']");
    const submitBtn = form.querySelector("button[type='submit']");

    // -------------------------
    // Gift note toggle
    // -------------------------
    const giftCheckbox = document.getElementById("isGift");
    const giftMessage = document.getElementById("giftMessage");

    giftCheckbox?.addEventListener("change", () => {
        giftMessage.style.display = giftCheckbox.checked ? "block" : "none";
    });

    // -------------------------
    // Gift wrap toggle
    // -------------------------
    const giftWrapCheckbox = document.getElementById("giftWrap");
    const giftPaperOptions = document.getElementById("giftPaperOptions");
    const giftWrapSummaryRow = document.getElementById("giftWrapSummaryRow");

    giftWrapCheckbox?.addEventListener("change", () => {
        const isWrapped = giftWrapCheckbox.checked;
        if (giftPaperOptions) giftPaperOptions.style.display = isWrapped ? "block" : "none";
        if (giftWrapSummaryRow) giftWrapSummaryRow.style.display = isWrapped ? "flex" : "none";
        updateTotals();
    });

    // -------------------------
    // Live shipping fee / total
    // -------------------------
    const EXPRESS_FEE = 149;
    const subtotalEl = document.getElementById("checkoutSubtotal");
    const shippingEl = document.getElementById("checkoutShipping");
    const totalEl = document.getElementById("checkoutTotal");
    const giftWrapFeeEl = document.getElementById("checkoutGiftWrapFee");
    const shippingRadios = form.querySelectorAll("input[name='shipping_option']");

    function parseRupees(text) {
        return parseFloat((text || "0").replace(/[^\d.]/g, "")) || 0;
    }

    function updateTotals() {
        if (!subtotalEl || !totalEl) return;

        const subtotal = parseRupees(subtotalEl.textContent);
        const selected = form.querySelector("input[name='shipping_option']:checked");
        const isExpress = selected && selected.value === "express";
        const fee = isExpress ? EXPRESS_FEE : 0;

        const wrapFee = (giftWrapCheckbox?.checked && giftWrapFeeEl)
            ? parseRupees(giftWrapFeeEl.textContent)
            : 0;

        if (shippingEl) {
            shippingEl.textContent = fee ? `₹${fee}` : "Free";
        }

        totalEl.textContent = `₹${subtotal + fee + wrapFee}`;
    }

    shippingRadios.forEach(radio => radio.addEventListener("change", updateTotals));
    updateTotals();

    // -------------------------
    // Trim inputs
    // -------------------------

    form.addEventListener("submit", (e) => {

        name.value = name.value.trim();
        phone.value = phone.value.trim();
        address.value = address.value.trim();

        // Name validation
        if (name.value.length < 2) {
            alert("Please enter a valid name.");
            e.preventDefault();
            return;
        }

        // Indian phone number validation
        const phoneRegex = /^[6-9]\d{9}$/;

        if (!phoneRegex.test(phone.value)) {

            alert("Please enter a valid 10-digit mobile number.");

            e.preventDefault();

            return;

        }

        // Address validation
        if (address.value.length < 10) {

            alert("Please enter a complete address.");

            e.preventDefault();

            return;

        }

        // Prevent double-click orders
        submitBtn.disabled = true;
        submitBtn.textContent = "Processing...";

    });

});