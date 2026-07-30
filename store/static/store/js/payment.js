document.addEventListener("DOMContentLoaded", () => {

    const screenshotInput = document.querySelector("input[name='screenshot']");
    const preview = document.getElementById("paymentPreview");

    if (screenshotInput && preview) {

        screenshotInput.addEventListener("change", function () {

            if (!this.files.length) return;

            const reader = new FileReader();

            reader.onload = function (e) {

                preview.src = e.target.result;

                preview.style.display = "block";

            };

            reader.readAsDataURL(this.files[0]);

        });

    }

    const form = document.querySelector(".payment-form");

    if (!form) return;

    form.addEventListener("submit", () => {

        const btn = form.querySelector("button[type='submit']");

        btn.disabled = true;

        btn.textContent = "Uploading...";

    });

});
const screenshot = document.getElementById("paymentScreenshot");
const preview = document.getElementById("paymentPreview");

if (screenshot && preview) {
    screenshot.addEventListener("change", function () {
        const file = this.files[0];

        if (!file) return;

        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
    });
}
const copyBtn = document.getElementById("copyUpi");

if (copyBtn) {
    copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(
            document.getElementById("upiId").textContent.trim()
        );

        copyBtn.textContent = "Copied ✓";

        setTimeout(() => {
            copyBtn.textContent = "Copy";
        }, 2000);
    });
}