import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand

# Exact load order currently in base.html — this MUST stay in this order,
# since several files rely on cascade order for their overrides to win
# (e.g. responsive.css's mobile breakpoints deliberately load last so they
# override the desktop-first rules in every other file).
CSS_LOAD_ORDER = [
    "cssvarient.css",
    "reset.css",
    "auth.css",
    "login.css",
    "base.css",
    "home.css",
    "header-nav.css",
    "hero-banner.css",
    "home-collections.css",
    "category.css",
    "home-trending.css",
    "home-categories.css",
    "home-bestsellers.css",
    "home-shop-the-look.css",
    "home-why-choose-us.css",
    "home-gift-personalized.css",
    "about.css",
    "product.css",
    "product-detail.css",
    "account-page.css",
    "whatsapp-widget.css",
    "cart-drawer.css",
    "size-guide.css",
    "checkout.css",
    "payment.css",
    "policy.css",
    "wishlist-popup.css",
    "wishlist-page.css",
    "product-grid.css",
    "footer.css",
    "responsive.css",
]


def minify_css(css):
    # Strip comments
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    # Collapse all whitespace runs (including newlines) to a single space
    css = re.sub(r"\s+", " ", css)
    # Remove whitespace directly touching punctuation that never needs it
    css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)
    # Drop the now-redundant trailing semicolon before a closing brace
    css = re.sub(r";}", "}", css)
    return css.strip()


class Command(BaseCommand):
    help = (
        "Bundles and minifies the site-wide CSS files (in CSS_LOAD_ORDER) "
        "into a single store/static/store/css/bundle.min.css. "
        "Re-run this any time you edit one of the source CSS files — "
        "base.html loads the bundle, not the individual files."
    )

    def handle(self, *args, **options):
        css_dir = os.path.join(settings.BASE_DIR, "store", "static", "store", "css")
        output_path = os.path.join(css_dir, "bundle.min.css")

        chunks = []
        missing = []

        for filename in CSS_LOAD_ORDER:
            path = os.path.join(css_dir, filename)
            if not os.path.isfile(path):
                missing.append(filename)
                continue
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks.append(f"/* --- {filename} --- */\n{minify_css(content)}")

        if missing:
            self.stderr.write(
                self.style.WARNING(
                    f"Skipped missing files (check CSS_LOAD_ORDER): {missing}"
                )
            )

        bundled = "\n".join(chunks)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(bundled)

        original_size = sum(
            os.path.getsize(os.path.join(css_dir, f))
            for f in CSS_LOAD_ORDER
            if os.path.isfile(os.path.join(css_dir, f))
        )
        new_size = os.path.getsize(output_path)

        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {output_path}\n"
                f"  {len(chunks)} files bundled, 1 request instead of {len(chunks)}\n"
                f"  {original_size:,} bytes -> {new_size:,} bytes "
                f"({(1 - new_size / original_size) * 100:.0f}% smaller)"
            )
        )
