"""
Standalone convenience wrapper for the CSS bundler.

Run from your project root (the folder containing manage.py):

    python bundle_css.py

This used to be a full standalone copy of the bundler with its own
CSS_LOAD_ORDER list — which quietly drifted out of sync with the real
one in store/management/commands/bundle_css.py (it was missing
payment.css and wishlist-popup.css, silently dropping them from every
bundle it produced). That's exactly the kind of duplicate-logic bug
this refactor is meant to eliminate, so this file now just calls the
one real implementation instead of keeping its own copy.

Prefer running the Django management command directly when you can:

    python manage.py bundle_css
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywebsite.settings")

import django
django.setup()

from store.management.commands.bundle_css import Command

if __name__ == "__main__":
    Command().handle()
