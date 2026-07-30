document.addEventListener("DOMContentLoaded", () => {
    initializeHeroSlider();
    initializeTrendingSlider();
    initializeShopLookModal();
    initializeNewsletterForm();
});
/*=========================================
NEWSLETTER FORM
=========================================*/

function initializeNewsletterForm() {

    const form = document.getElementById("newsletterForm");
    const msg = document.getElementById("newsletterMsg");

    const overlay = document.getElementById("newsletterSuccessOverlay");
    const closeBtn = document.getElementById("newsletterSuccessClose");
    const continueBtn = document.getElementById("newsletterSuccessContinue");

    if (!form) return;

    function showSuccessModal() {
        overlay?.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function hideSuccessModal() {
        overlay?.classList.remove("active");
        document.body.style.overflow = "";
    }

    closeBtn?.addEventListener("click", hideSuccessModal);
    continueBtn?.addEventListener("click", hideSuccessModal);
    overlay?.addEventListener("click", (e) => {
        if (e.target === overlay) hideSuccessModal();
    });

    form.addEventListener("submit", (e) => {

        e.preventDefault();

        const formData = new FormData(form);
        const submitBtn = form.querySelector("button[type=submit]");

        submitBtn?.classList.add("loading");
        submitBtn?.setAttribute("disabled", "disabled");

        fetch(form.action, {
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            body: formData,
        })
        .then(res => res.json())
        .then(data => {

            if (data.success) {
                form.reset();
                showSuccessModal();
            } else if (msg) {
                msg.textContent = data.error || "Something went wrong. Please try again.";
            }

        })
        .catch(() => {
            if (msg) msg.textContent = "Something went wrong. Please try again.";
        })
        .finally(() => {
            submitBtn?.classList.remove("loading");
            submitBtn?.removeAttribute("disabled");
        });

    });

}


/*=========================================
HERO SLIDER
=========================================*/

function initializeHeroSlider() {

    const slides = document.querySelectorAll(".hero-slide");
    const dots = document.querySelectorAll(".hero-dot");
    const prev = document.querySelector(".hero-prev");
    const next = document.querySelector(".hero-next");

    if (!slides.length) return;

    let current = 0;
    let timer;

    function showSlide(index) {

        slides.forEach(slide =>
            slide.classList.remove("active")
        );

        dots.forEach(dot =>
            dot.classList.remove("active")
        );

        slides[index].classList.add("active");

        if (dots[index]) {
            dots[index].classList.add("active");
        }

        current = index;
    }

    function nextSlide() {

        current++;

        if (current >= slides.length) {
            current = 0;
        }

        showSlide(current);

    }

    function previousSlide() {

        current--;

        if (current < 0) {
            current = slides.length - 1;
        }

        showSlide(current);

    }

    function startSlider() {

        timer = setInterval(nextSlide, 5000);

    }

    function resetTimer() {

        clearInterval(timer);
        startSlider();

    }

    next?.addEventListener("click", () => {

        nextSlide();
        resetTimer();

    });

    prev?.addEventListener("click", () => {

        previousSlide();
        resetTimer();

    });

    dots.forEach((dot, index) => {

        dot.addEventListener("click", () => {

            showSlide(index);
            resetTimer();

        });

    });

    showSlide(0);
    startSlider();

}


/*=========================================
TRENDING PRODUCTS SLIDER
=========================================*/

function initializeTrendingSlider() {

    const slider = document.querySelector(".trending-slider");

    const prev = document.querySelector(".product-card-prev");
    const next = document.querySelector(".product-card-next");

    if (!slider) return;

    const scrollAmount = 320;

    next?.addEventListener("click", () => {

        slider.scrollBy({

            left: scrollAmount,
            behavior: "smooth"

        });

    });

    prev?.addEventListener("click", () => {

        slider.scrollBy({

            left: -scrollAmount,
            behavior: "smooth"

        });

    });

}


/*=========================================
SHOP THIS LOOK MODAL
=========================================*/

function initializeShopLookModal() {

    const modal = document.getElementById("lookModal");

    if (!modal) return;

    window.openLook = function(id) {

        modal.style.display = "flex";

        document.body.style.overflow = "hidden";

        document
            .querySelectorAll(".modal-content")
            .forEach(item => item.style.display = "none");

        const selected = document.getElementById("look" + id);

        if (selected) {
            selected.style.display = "block";
        }

    };

    window.closeLook = function() {

        modal.style.display = "none";

        document.body.style.overflow = "";

    };

    modal.addEventListener("click", function(e){

        if(e.target === modal){

            closeLook();

        }

    });

    document.getElementById("closeLookBtn")?.addEventListener("click", closeLook);

    document.addEventListener("keydown", function(e){

        if(e.key === "Escape"){

            closeLook();

        }

    });

}
document.querySelectorAll(".look-card").forEach(card => {
    card.addEventListener("click", () => {
        openLook(card.dataset.lookId);
    });
});