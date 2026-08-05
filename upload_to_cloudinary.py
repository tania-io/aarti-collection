import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mywebsite.settings")

import django
django.setup()

from decouple import config
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
    secure=True,
)

from store.models import Product

uploaded = 0
skipped = 0

for product in Product.objects.all():
    if not product.image:
        continue

    local_path = product.image.path

    if not os.path.exists(local_path):
        print(f"Missing: {local_path}")
        skipped += 1
        continue

    print(f"Uploading {local_path}")

    result = cloudinary.uploader.upload(
        local_path,
        folder="products",
    )

    product.image = result["public_id"]
    product.save(update_fields=["image"])

    uploaded += 1

print("\nFinished")
print("Uploaded:", uploaded)
print("Skipped:", skipped)