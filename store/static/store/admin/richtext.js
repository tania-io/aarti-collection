(function () {

    function initRichTextEditor(wrap) {

        const targetId = wrap.dataset.target;
        const textarea = document.getElementById(targetId);
        const surface = wrap.querySelector(".richtext-surface");
        const imageInput = wrap.querySelector(".richtext-image-input");

        if (!textarea || !surface) return;

        // Hide the raw textarea — it stays in the DOM as the real form value
        textarea.style.display = "none";

        surface.innerHTML = textarea.value || "<p></p>";

        function syncToTextarea() {
            textarea.value = surface.innerHTML;
        }

        surface.addEventListener("input", syncToTextarea);
        surface.addEventListener("blur", syncToTextarea);

        // Make sure the value is fresh no matter how the form gets submitted
        const form = wrap.closest("form");
        form?.addEventListener("submit", syncToTextarea);

        // ==========================
        // Toolbar
        // ==========================

        wrap.querySelectorAll(".richtext-toolbar button[data-cmd]").forEach(btn => {

            btn.addEventListener("click", () => {
                surface.focus();
                document.execCommand(btn.dataset.cmd, false, btn.dataset.value || null);
                syncToTextarea();
            });

        });

        wrap.querySelectorAll(".richtext-toolbar button[data-action]").forEach(btn => {

            btn.addEventListener("click", () => {

                const action = btn.dataset.action;

                if (action === "link") {
                    const url = window.prompt("Link URL:", "https://");
                    if (url) {
                        surface.focus();
                        document.execCommand("createLink", false, url);
                        syncToTextarea();
                    }
                    return;
                }

                if (action === "image") {
                    imageInput.click();
                    return;
                }

                if (action === "table") {
                    surface.focus();
                    const tableHtml =
                        "<table class='policy-table'><tbody>" +
                        "<tr><td>Cell 1</td><td>Cell 2</td></tr>" +
                        "<tr><td>Cell 3</td><td>Cell 4</td></tr>" +
                        "</tbody></table><p></p>";
                    document.execCommand("insertHTML", false, tableHtml);
                    syncToTextarea();
                    return;
                }

                if (action === "card") {
                    surface.focus();
                    const cardHtml =
                        "<div class='policy-card'><h3>Card heading</h3>" +
                        "<p>Card content goes here.</p></div><p></p>";
                    document.execCommand("insertHTML", false, cardHtml);
                    syncToTextarea();
                    return;
                }

                if (action === "preview") {
                    const isPreview = wrap.classList.toggle("richtext-preview-mode");
                    surface.setAttribute("contenteditable", isPreview ? "false" : "true");
                    btn.classList.toggle("active", isPreview);
                    return;
                }

            });

        });

        // ==========================
        // Image upload (embedded as base64 — no upload endpoint needed)
        // ==========================

        imageInput?.addEventListener("change", function () {

            if (!this.files.length) return;

            const reader = new FileReader();

            reader.onload = (event) => {
                surface.focus();
                document.execCommand(
                    "insertHTML",
                    false,
                    `<img src="${event.target.result}" alt="" style="max-width:100%;border-radius:8px;">`
                );
                syncToTextarea();
            };

            reader.readAsDataURL(this.files[0]);
            this.value = "";

        });

    }

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".richtext-wrap").forEach(initRichTextEditor);
    });

})();
