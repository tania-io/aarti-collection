/*
=========================================
AARTI COLLECTION
Main JavaScript
=========================================
*/

document.addEventListener("DOMContentLoaded", () => {

    initializeMobileMenu();
    initializeMobileCategories();
    initializeMobileSearch();
    initializeAnimatedSearchPlaceholder();
    initializeCartDrawer();
    initializeStickyHeader();
    initializeFlashMessages();
    initializeSmoothScroll();
    initializeEscapeKey();

});


/*=========================================
Helpers
=========================================*/

let _lockedScrollY = 0;

function lockBody() {
    _lockedScrollY = window.scrollY;
    document.body.style.position = "fixed";
    document.body.style.top = `-${_lockedScrollY}px`;
    document.body.style.left = "0";
    document.body.style.right = "0";
    document.body.style.width = "100%";
    document.body.style.overflow = "hidden";
}

function unlockBody() {
    document.body.style.position = "";
    document.body.style.top = "";
    document.body.style.left = "";
    document.body.style.right = "";
    document.body.style.width = "";
    document.body.style.overflow = "";
    window.scrollTo(0, _lockedScrollY);
}

window.lockBody = lockBody;
window.unlockBody = unlockBody;


/*=========================================
Mobile Menu
=========================================*/

function initializeMobileMenu() {

    const menu = document.getElementById("mobileMenu");
    const overlay = document.getElementById("mobileOverlay");
    const openBtn = document.getElementById("menuToggle");
    const closeBtn = document.getElementById("closeMenu");

    if (!menu || !openBtn) return;

    function openMenu() {

        menu.classList.add("active");
        overlay.classList.add("active");

        lockBody();

    }

    function closeMenu() {

        menu.classList.remove("active");
        overlay.classList.remove("active");

        unlockBody();

    }

    openBtn.addEventListener("click", openMenu);

    closeBtn?.addEventListener("click", closeMenu);

    overlay?.addEventListener("click", closeMenu);

}


/*=========================================
Mobile Categories
=========================================*/
function initializeMobileCategories() {

    const buttons = document.querySelectorAll(".mobile-category-btn");

    buttons.forEach(button => {

        button.addEventListener("click", function () {

            const submenu = this.nextElementSibling;

            if (!submenu) return;

            this.classList.toggle("active");
            submenu.classList.toggle("active");

            this.setAttribute(
                "aria-expanded",
                submenu.classList.contains("active")
            );

        });

    });

}
/*=========================================
Mobile Search
=========================================*/

function initializeMobileSearch() {

    const button = document.getElementById("mobileSearchToggle");
    const form = document.getElementById("mobileSearchForm");
    const closeBtn = document.getElementById("closeMobileSearch");

    if (!button || !form) return;

    button.addEventListener("click", () => {

        form.classList.toggle("active");

    });

    closeBtn?.addEventListener("click", () => {

        form.classList.remove("active");

    });

}

function initializeAnimatedSearchPlaceholder() {

    const inputs = document.querySelectorAll(".search-input-animated");

    if (!inputs.length) return;

    const words = [
        "products", "bangles", "earrings", "necklaces",
        "anklets", "rings", "gift boxes"
    ];

    let index = 0;

    setInterval(() => {

        index = (index + 1) % words.length;

        inputs.forEach(input => {

            if (document.activeElement === input || input.value) return;

            input.placeholder = `Search for ${words[index]}...`;

        });

    }, 2200);

}


/*=========================================
Cart Drawer
=========================================*/

function initializeCartDrawer() {

    const drawer = document.getElementById("cartDrawer");
    const overlay = document.getElementById("cartOverlay");

    const openBtn = document.getElementById("cartToggle");
    const closeBtn = document.getElementById("closeCart");

    if (!drawer || !openBtn) return;

    function openCart(e) {

        e.preventDefault();

        drawer.classList.add("active");

        overlay.classList.add("active");

        lockBody();

    }

    function closeCart() {

        drawer.classList.remove("active");

        overlay.classList.remove("active");

        unlockBody();

    }

    openBtn.addEventListener("click", openCart);

    closeBtn?.addEventListener("click", closeCart);

    overlay?.addEventListener("click", closeCart);

    const copyLinkBtn = document.getElementById("copyCartLink");

    copyLinkBtn?.addEventListener("click", () => {

        navigator.clipboard?.writeText(window.location.origin + "/cart/")
            .then(() => {
                const original = copyLinkBtn.textContent;
                copyLinkBtn.textContent = "✓";
                setTimeout(() => { copyLinkBtn.textContent = original; }, 1500);
            })
            .catch(() => {});

    });

}


/*=========================================
Sticky Header
=========================================*/

function initializeStickyHeader() {

    const header = document.querySelector(".sticky-header");

    if (!header) return;

    window.addEventListener("scroll", () => {

        header.classList.toggle("scrolled", window.scrollY > 20);

    });

}


/*=========================================
Flash Messages
=========================================*/

function initializeFlashMessages() {

    document.querySelectorAll(".message,.alert,.success-message").forEach(message => {

        setTimeout(() => {

            message.style.opacity = "0";

            setTimeout(() => message.remove(), 300);

        }, 3500);

    });

}


/*=========================================
Smooth Scroll
=========================================*/

function initializeSmoothScroll() {

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (!target) return;

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth"

            });

        });

    });

}


/*=========================================
Escape Key
=========================================*/

function initializeEscapeKey() {

    document.addEventListener("keydown", e => {

        if (e.key !== "Escape") return;

        document.getElementById("mobileMenu")?.classList.remove("active");
        document.getElementById("mobileOverlay")?.classList.remove("active");

        document.getElementById("cartDrawer")?.classList.remove("active");
        document.getElementById("cartOverlay")?.classList.remove("active");

        document.getElementById("wishlistModal")?.classList.remove("active");
        document.getElementById("wishlistOverlay")?.classList.remove("active");

        unlockBody();

    });

}


/*=========================================
CSRF
=========================================*/

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

                break;

            }

        }

    }

    return cookieValue;

}

window.getCookie = getCookie;