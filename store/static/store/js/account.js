document.addEventListener("DOMContentLoaded", () => {

    const drawer = document.getElementById("profileDrawer");
    const overlay = document.getElementById("drawerOverlay");

    const openDrawer = document.getElementById("openDrawer");
    const openDrawerCard = document.getElementById("openDrawerCard");
    const closeDrawer = document.getElementById("closeDrawer");
    const closeDrawer2 = document.getElementById("closeDrawer2");

    const deleteModal = document.getElementById("deleteModal");
    const deleteBtn = document.getElementById("deleteAccountBtn");
    const cancelDelete = document.getElementById("cancelDelete");

    const logoutModal = document.getElementById("logoutModal");
    const logoutBtn = document.getElementById("logoutBtn");
    const cancelLogout = document.getElementById("cancelLogout");

    const imageInput = document.getElementById("profile_image");
    const previewImage = document.getElementById("previewImage");

    function closeEverything() {
        drawer?.classList.remove("open");
        overlay?.classList.remove("show");
        deleteModal?.classList.remove("show");
        logoutModal?.classList.remove("show");
    }

    // -------------------------
    // Drawer
    // -------------------------

    function openProfileDrawer() {
        drawer?.classList.add("open");
        overlay?.classList.add("show");
    }

    openDrawer?.addEventListener("click", openProfileDrawer);
    openDrawerCard?.addEventListener("click", openProfileDrawer);

    closeDrawer?.addEventListener("click", closeEverything);
    closeDrawer2?.addEventListener("click", closeEverything);

    overlay?.addEventListener("click", closeEverything);

    // -------------------------
    // Delete Modal
    // -------------------------

    deleteBtn?.addEventListener("click", () => {
        deleteModal?.classList.add("show");
        overlay?.classList.add("show");
    });

    cancelDelete?.addEventListener("click", closeEverything);

    // -------------------------
    // Logout Modal
    // -------------------------

    logoutBtn?.addEventListener("click", () => {
        logoutModal?.classList.add("show");
        overlay?.classList.add("show");
    });

    cancelLogout?.addEventListener("click", closeEverything);

    // -------------------------
    // Image Preview
    // -------------------------

    imageInput?.addEventListener("change", function () {

        if (!this.files.length) return;

        const reader = new FileReader();

        reader.onload = function (event) {
            previewImage.src = event.target.result;
        };

        reader.readAsDataURL(this.files[0]);

    });
    // ESC closes everything

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeEverything();
        }

    });

});