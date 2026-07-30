document.addEventListener("DOMContentLoaded", () => {

    /* ==========================
       GRID / LIST VIEW
       (Filter drawer, sort menu, and accordions are all owned by
       category.js — kept in one place to avoid duplicate/competing
       listeners on the same elements.)
    ========================== */

    const collection = document.getElementById("productGrid");

    document.querySelectorAll(".view-btn").forEach(button => {

        button.addEventListener("click", function () {

            document
                .querySelectorAll(".view-btn")
                .forEach(btn => btn.classList.remove("active"));

            this.classList.add("active");

            if (!collection) return;

            if (this.dataset.view === "list") {
                collection.classList.add("list-view");
            } else {
                collection.classList.remove("list-view");
            }

        });

    });

    /* ==========================
       PRODUCT PREVIEW VIDEOS
       Autoplay muted loop, but only once the card is actually in view
       (lazy) so we're not downloading/decoding dozens of clips at once.
       Falls back to the poster image if the browser can't play it.
    ========================== */

    const lazyVideos = document.querySelectorAll("video[data-lazy-video]");

    if (lazyVideos.length) {

        const io = new IntersectionObserver((entries) => {

            entries.forEach(entry => {

                const video = entry.target;

                if (entry.isIntersecting) {

                    const source = video.querySelector("source[data-src]");

                    if (source && !source.src) {
                        source.src = source.dataset.src;
                        video.load();
                    }

                    video.play()
                        .then(() => video.classList.add("pg-video-active"))
                        .catch(() => {
                            // Autoplay blocked or file failed to decode —
                            // keep showing the poster image, no blank box.
                            video.classList.remove("pg-video-active");
                        });

                } else {
                    video.pause();
                    video.classList.remove("pg-video-active");
                }

            });

        }, { rootMargin: "100px" });

        lazyVideos.forEach(video => io.observe(video));
    }

});
