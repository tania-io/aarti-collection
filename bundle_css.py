"""
Standalone CSS bundler for Aarti Collection.

Run this from your project root (the folder containing manage.py):

    python bundle_css.py

It does not need Django to discover it as a management command — it just
reads the CSS files directly off disk. Use this any time you edit one of
the source CSS files in store/static/store/css/, since base.html loads
the bundled bundle.min.css, not the individual files.
"""

import os
import re

# Must match store/management/commands/bundle_css.py exactly — this is
# the same load order as base.html originally used, and order matters:
# responsive.css deliberately loads last so its mobile overrides win.
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
    "policy.css",
    "wishlist-page.css",
    "product-grid.css",
    "footer.css",
    "responsive.css",
]


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return css.strip()


def find_css_dir():
    # Look for store/static/store/css relative to wherever this script is run from
    candidates = [
        os.path.join("store", "static", "store", "css"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "store", "static", "store", "css"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    raise SystemExit(
        "Could not find store/static/store/css — run this script from your "
        "project root (the folder containing manage.py)."
    )


def main():
    css_dir = find_css_dir()
    output_path = os.path.join(css_dir, "bundle.min.css")

    chunks = []
    missing = []
    original_size = 0

    for filename in CSS_LOAD_ORDER:
        path = os.path.join(css_dir, filename)
        if not os.path.isfile(path):
            missing.append(filename)
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        original_size += os.path.getsize(path)
        chunks.append(f"/* --- {filename} --- */\n{minify_css(content)}")

    if missing:
        print(f"WARNING: skipped missing files: {missing}")

    bundled = "\n".join(chunks)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(bundled)

    new_size = os.path.getsize(output_path)
    print(f"Wrote {output_path}")
    print(f"{len(chunks)} files bundled, {original_size:,} -> {new_size:,} bytes "
          f"({(1 - new_size / original_size) * 100:.0f}% smaller)")


if __name__ == "__main__":
    main()
