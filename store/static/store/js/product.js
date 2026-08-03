/*
=========================================
PRODUCT PAGE
=========================================
*/

document.addEventListener("DOMContentLoaded", () => {

    initializeGallery();
    initializeReviewAttachments();

});


/*=========================================
REVIEW PHOTO ATTACHMENTS (live preview)
=========================================*/

function initializeReviewAttachments() {

    const input = document.getElementById("reviewAttachments");
    const preview = document.getElementById("reviewAttachPreview");

    if (!input || !preview) return;

    let selectedFiles = [];

    function render() {

        preview.innerHTML = "";

        selectedFiles.forEach((file, index) => {

            const thumb = document.createElement("div");
            thumb.className = "review-attach-thumb";

            const img = document.createElement("img");
            img.src = URL.createObjectURL(file);
            img.alt = file.name;

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.setAttribute("aria-label", "Remove photo");
            removeBtn.textContent = "×";

            removeBtn.addEventListener("click", () => {
                selectedFiles.splice(index, 1);
                syncInput();
                render();
            });

            thumb.appendChild(img);
            thumb.appendChild(removeBtn);
            preview.appendChild(thumb);

        });

    }

    function syncInput() {

        // Keep the real <input type="file"> in sync with our own
        // selectedFiles array so removing a preview actually removes
        // it from what gets submitted.
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(file => dataTransfer.items.add(file));
        input.files = dataTransfer.files;

    }

    input.addEventListener("change", () => {

        const incoming = Array.from(input.files);
        selectedFiles = [...selectedFiles, ...incoming].slice(0, 5);

        syncInput();
        render();

    });

}


/*=========================================
IMAGE GALLERY (thumbnails + colour-linked filtering)
=========================================*/

function initializeGallery() {

    const mainImage = document.getElementById("mainProductImage");
    const mainVideo = document.getElementById("mainProductVideo");
    const slidesEl = document.getElementById("gallery-slides-data");
    const thumbRail = document.getElementById("galleryThumbs");
    const colourNameEl = document.getElementById("selectedColourName");

    if (!mainImage || !slidesEl) return;

    let allSlides = [];

    try {
        allSlides = JSON.parse(slidesEl.textContent) || [];
    } catch (e) {
        allSlides = [];
    }

    if (!allSlides.length) return;

    let activeVariant = allSlides.some(s => s.variant === 0) ? 0 : null;
    let visibleSlides = [];
    let currentIndex = 0;

    function slidesForVariant(variantIndex) {
        // Images tied to the selected colour, plus any un-tied (variant: null) slides (e.g. video)
        return allSlides.filter(s => s.variant === variantIndex || s.variant === null);
    }

    function renderThumbs() {

        if (!thumbRail) return;

        thumbRail.innerHTML = "";

        visibleSlides.forEach((slide, i) => {

            const thumb = document.createElement("button");
            thumb.type = "button";
            thumb.className = "gallery-thumb" + (i === currentIndex ? " active" : "");
            thumb.setAttribute("aria-label", slide.type === "video" ? "Play video" : "View image " + (i + 1));

            if (slide.type === "video") {
                thumb.innerHTML = '<span class="thumb-play">▶</span>';
                thumb.style.background = "#222";
            } else {
                const img = document.createElement("img");
                img.src = slide.src;
                img.alt = "";
                thumb.appendChild(img);
            }

            thumb.addEventListener("click", () => showSlide(i));

            thumbRail.appendChild(thumb);

        });

    }

    function showSlide(index) {

        if (!visibleSlides[index]) return;

        currentIndex = index;

        const slide = visibleSlides[index];

        if (slide.type === "video") {

            mainVideo.src = slide.src;
            mainVideo.style.display = "block";
            mainImage.style.display = "none";

        } else {

            mainVideo.pause();
            mainVideo.removeAttribute("src");
            mainVideo.style.display = "none";
            mainImage.style.display = "block";
            mainImage.src = slide.src;

        }

        thumbRail?.querySelectorAll(".gallery-thumb").forEach((t, i) => {
            t.classList.toggle("active", i === index);
        });

    }

    function nextSlide() {
        showSlide((currentIndex + 1) % visibleSlides.length);
    }

    function previousSlide() {
        showSlide((currentIndex - 1 + visibleSlides.length) % visibleSlides.length);
    }

    function selectVariant(variantIndex, colourName) {

        activeVariant = variantIndex;
        visibleSlides = slidesForVariant(variantIndex);

        document.querySelectorAll(".colour-dot").forEach(dot => {
            dot.classList.toggle(
                "active",
                parseInt(dot.dataset.variantIndex, 10) === variantIndex
            );
        });

        if (colourNameEl && colourName) {
            colourNameEl.textContent = ": " + colourName;
        }

        const activeDot = document.querySelector(
            `.colour-dot[data-variant-index="${variantIndex}"]`
        );
        const variantId = activeDot?.dataset.variantId;

        if (variantId) {
            document.querySelector(".add-cart-btn")?.setAttribute("data-variant-id", variantId);
            document.querySelector(".buy-btn")?.setAttribute("data-variant-id", variantId);
        }

        renderThumbs();
        showSlide(0);

    }

    // Initial state
    visibleSlides = activeVariant !== null ? slidesForVariant(activeVariant) : allSlides;
    renderThumbs();
    showSlide(0);

    document.addEventListener("keydown", e => {
        if (e.key === "ArrowRight") nextSlide();
        if (e.key === "ArrowLeft") previousSlide();
    });

    let touchStart = 0;
    let touchEnd = 0;

    mainImage.addEventListener("touchstart", e => {
        touchStart = e.changedTouches[0].screenX;
    });

    mainImage.addEventListener("touchend", e => {
        touchEnd = e.changedTouches[0].screenX;
        if (touchEnd < touchStart - 40) nextSlide();
        if (touchEnd > touchStart + 40) previousSlide();
    });

    document.querySelector(".gallery-arrow.right")
        ?.addEventListener("click", nextSlide);

    document.querySelector(".gallery-arrow.left")
        ?.addEventListener("click", previousSlide);

    document.querySelectorAll(".colour-dot").forEach(dot => {

        dot.addEventListener("click", () => {

            if (dot.classList.contains("disabled")) return;

            const index = parseInt(dot.dataset.variantIndex, 10);

            if (!isNaN(index)) {
                selectVariant(index, dot.dataset.colourName);
            }

        });

    });

}

/* ==========================
   IMAGE ZOOM LIGHTBOX
========================== */
document.addEventListener("DOMContentLoaded", () => {

    const zoomBtn = document.getElementById("galleryZoomBtn");
    const mainImg = document.getElementById("mainProductImage");
    const lightbox = document.getElementById("galleryLightbox");
    const lightboxImg = document.getElementById("galleryLightboxImage");
    const closeBtn = document.getElementById("galleryLightboxClose");

    if (!zoomBtn || !lightbox) return;

    function openZoom() {
        lightboxImg.src = mainImg.src;
        lightbox.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeZoom() {
        lightbox.classList.remove("active");
        document.body.style.overflow = "";
    }

    zoomBtn.addEventListener("click", openZoom);
    mainImg?.addEventListener("click", openZoom);
    closeBtn?.addEventListener("click", closeZoom);

    lightbox.addEventListener("click", (e) => {
        if (e.target === lightbox) closeZoom();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeZoom();
    });

});

/* ==========================
   PRODUCT DETAILS ACCORDION
   (Description / Product Details / Care Instructions)
========================== */
document.addEventListener("DOMContentLoaded", () => {

    const accordion = document.getElementById("pdAccordion");
    if (!accordion) return;

    const items = Array.from(accordion.querySelectorAll(".pd-accordion-item"));
    const storageKey = "pd-accordion-panel:" + (accordion.dataset.productSlug || "");

    function openPanel(item, remember) {

        items.forEach(other => {
            const isTarget = other === item;
            other.classList.toggle("active", isTarget);

            const toggle = other.querySelector(".pd-accordion-toggle");
            const icon = other.querySelector(".pd-accordion-icon");

            toggle?.setAttribute("aria-expanded", isTarget ? "true" : "false");
            if (icon) icon.textContent = isTarget ? "−" : "+";
        });

        if (remember) {
            try {
                sessionStorage.setItem(storageKey, item.dataset.panel);
            } catch (e) {
                // sessionStorage unavailable (private browsing etc.) — not critical
            }
        }
    }

    items.forEach(item => {
        item.querySelector(".pd-accordion-toggle")?.addEventListener("click", () => {
            openPanel(item, true);
        });
    });

    // Restore the panel the user had open last time, if any
    try {
        const savedPanel = sessionStorage.getItem(storageKey);
        if (savedPanel) {
            const match = items.find(item => item.dataset.panel === savedPanel);
            if (match) openPanel(match, false);
        }
    } catch (e) {
        // ignore
    }

});
